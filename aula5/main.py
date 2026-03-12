from fastapi import FastAPI, Request, Depends, HTTPException, status, Cookie, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from typing import Annotated
import logging
import time


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

def db_search_first(db, table: str, fn, _else=None):
    for row in db[table]:
        if fn(row):
            return row

    return _else

class User(BaseModel):
    name: str
    password: str
    bio: str

class UserLogin(BaseModel):
    name: str
    password: str

    def match_with_user(self, user):
        return self.name == user.name and self.password == user.password

OUR_DB = {"users": []}

def get_active_user(session_user: Annotated[str | None, Cookie()] = None):
    # O FastAPI busca automaticamente um cookie chamado 'session_user'
    if not session_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Acesso negado: você não está logado."
        )
    
    user = next((u for u in OUR_DB['users'] if u.name == session_user), None)
    if not user:
        raise HTTPException(status_code=401, detail="Sessão inválida")
    
    return user
    
@app.get("/")
def create_user_html(request: Request):
    """retorna um template com o formulário de criação de usuário"""
    return templates.TemplateResponse(
        request=request, name="user_create.html", context={"user": None}
    )

@app.post("/users")
async def create_user(user: User, response: Response):
    """rota que vai criar usuários novos a partir do formulário"""
    OUR_DB['users'].append(user)
    response.set_cookie(key="session_user", value=user.name)
    return {"status": "sucesso", "usuario": user}
    
@app.get("/login")
async def login_user(request: Request):
    """retorna um template com o formulário de login"""
    return templates.TemplateResponse(
        request=request, name="user_login.html"
    )

    
@app.post("/login")
async def login(user: UserLogin, response: Response):
    """recebe dados do formulário de login e retorna cookie de sessão"""

    usuario_encontrado = db_search_first(OUR_DB, 'users', user.match_with_user)
    
    if usuario_encontrado is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    response.set_cookie(key="session_user", value=user.name)
    return {"msg": "Logado com sucesso"}
    
@app.get("/home")
async def show_profile(request: Request, user: dict = Depends(get_active_user)):
    """rota protegida com o depends que depende do cookie de sessão"""
    return templates.TemplateResponse(
        request=request, 
        name="user_view.html", 
        context={"username": user.name, "bio": user.bio}
    )

