from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field



class User(BaseModel):
    name: str = Field(alias="nome")
    age: int = Field(alias="idade")

    def __str__(self):
        return f"Usuário {self.name} de idade {self.age}"

app = FastAPI()

OUR_DB = {"users": []}

def read_html_file(name: str):
    filename = f"{name}.html"

    with open(filename, "r") as file:
        data = file.read()

    return data

INDEX_HTML_CONTENT = read_html_file("index")

@app.get("/", response_class=HTMLResponse)
async def index():
    """Envia a página HTML abaixo para o usuário"""

    return INDEX_HTML_CONTENT

@app.post("/users", response_class=HTMLResponse)
async def add_user(user: User):
    """Adiciona um usuário numa lista"""
    OUR_DB["users"].append(user)
    return str(user) + " foi criado"
    
@app.get("/users", response_class=HTMLResponse)
async def list_user(index: int | None = None):
    """Lê todos os usuários da lista ou um índice específico (usando query parameter)"""
    if index is None:
        return '<br />'.join(str(user) for user in OUR_DB["users"])
    if index in OUR_DB["users"]:
        user = OUR_DB["users"][index]
        return str(user)

    return "Erro: Índice inesperado"
    
@app.delete("/users", response_class=HTMLResponse)
async def clear_user():
    """Limpa a lista de usuários"""
    OUR_DB["users"] = []
    return "A lista de usuários foi limpo"

