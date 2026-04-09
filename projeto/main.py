from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session, select, SQLModel, create_engine
from models import Run, User, FoodOpnion, Menu
from utils import run_bandex
from datetime import datetime, timedelta
from typing import Annotated


arquivo_sqlite = "projeto.db"
url_sqlite = f"sqlite:///{arquivo_sqlite}"
engine = create_engine(url_sqlite)

templates = Jinja2Templates(directory=["templates"])

def create_db_and_tables():
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
def on_startup() -> None:
    create_db_and_tables()


def get_menus(request, menu_date, menu_types):
    run_bandex(engine)

    with Session(engine) as session:
        results = {}
        for menu_type in menu_types:
            statement = select(Menu).where(Menu.date == menu_date.date()).where(Menu.menu_type == menu_type)
            results[menu_type] = session.exec(statement).all()

    return results

@app.get("/",response_class=HTMLResponse)
async def root(request: Request):
    run_bandex(engine)

    date = datetime.today()

    if date.hour < 14:
        menu_types = ("Almoço",)
    elif date.hour < 20:
        menu_types = ("Jantar",)
    else:
        menu_types = ("Almoço", "Jantar")

    with Session(engine) as session:
        results = session.exec(select(Menu))
        dates = list(set(
            (f"{result.date:%Y-%m-%d}", f"{result.date:%d/%m/%Y}") for result in results
        ))

    dates.sort()

    return templates.TemplateResponse(request, "index.html", { "dates": dates, "date": date, "menu_types": menu_types })

@app.get("/menu", response_class=HTMLResponse)
async def get_menu_page(request: Request, date: Annotated[str, Form()] | None = None,
                        menuTypes: Annotated[str, Form()] | None = None,
                        login: Annotated[str, Form()] | None = None):
    if not "HX-Request" in request.headers:
        return RedirectResponse(url="/")

    print(date)

    if date is None:
        date = datetime.today()

        if menuTypes is None:
            if date.hour < 14:
                menu_types = ("Almoço",)
            elif date.hour < 20:
                menu_types = ("Jantar",)
            else:
                menu_types = ("Almoço", "Jantar")
        elif menuTypes == '':
            menu_types = ("Almoço", "Jantar")
        else:
            menu_types = menuTypes.split(';')
    else:
        date = datetime.strptime(date, "%Y-%m-%d")

        if menuTypes is None:
            if date.hour < 14:
                menu_types = ("Almoço",)
            elif date.hour < 20:
                menu_types = ("Jantar",)
            else:
                menu_types = ("Almoço", "Jantar")
        elif menuTypes == '':
            menu_types = ("Almoço", "Jantar")
        else:
            menu_types = menuTypes.split(';')

    menus = get_menus(request, date, menu_types)

    with Session(engine) as session:
        if login is None or login == '':
            food_opnions = []
        else:
            user = session.exec(select(User).where(User.login == login)).first()
            statement = select(FoodOpnion).where(FoodOpnion.owner == user)
            results = session.exec(statement)

            food_opnions = results.all()

    for menu_type in menus:
        for menu in menus[menu_type]:
            if menu.content.lower() == "fechado":
                menu.state = "closed"
            content = []

            for line in menu.content.replace(", ", "\n").replace(",", "\n").split("\n"):
                line = line.strip().removeprefix("Opção: ")

                if line == '' or (line.startswith("**") and line.endswith("**")):
                    continue

                opnion = None
                for food_opnion in food_opnions:
                    if line == food_opnion.food_name:
                        opnion = food_opnion.liked
                        break


                content.append((line, opnion))

            menu.content = content

    return templates.TemplateResponse(request, "menu.html", { "menus": menus })


@app.post("/login")
async def do_login(login: Annotated[str, Form()], request: Request):
    if not "HX-Request" in request.headers:
        return RedirectResponse(url="/")

    with Session(engine) as session:
        statement = select(User).where(User.login == login)
        user = session.exec(statement).first()

        if user is None:
            user = User(login=login)
            session.add(user)
            session.commit()
            session.refresh(user)

    return templates.TemplateResponse(request, "logout.html", { "user": user })

@app.get("/login")
def do_logout(request: Request):
    return templates.TemplateResponse(request, "login.html", {})

@app.post("/food-opnion")
async def create_food_opnion(name: Annotated[str, Form()], liked: Annotated[bool, Form()], login: Annotated[str, Form()], id: Annotated[int, Form()], request: Request):
    if not "HX-Request" in request.headers:
        return RedirectResponse(url="/")

    with Session(engine) as session:
        statement = select(User).where(User.login == login)
        user = session.exec(statement).first()

        fo = FoodOpnion(owner_id=user.id, food_name=name, liked=liked)

        session.add(fo)
        session.commit()
        session.refresh(fo)

    return templates.TemplateResponse(request, "food-opnion.html", { "food_opnion": fo.liked, "name": name, "id": id })


@app.delete("/food-opnion")
async def delete_food_opnion(name: str, login: str, id: int, request: Request):
    if not "HX-Request" in request.headers:
        return RedirectResponse(url="/")

    with Session(engine) as session:
        statement = select(User).where(User.login == login)
        user = session.exec(statement).first()

        statement = select(FoodOpnion).where(FoodOpnion.food_name == name)
        fo = session.exec(statement).first()

        if fo:
            session.delete(fo)
            session.commit()

    return templates.TemplateResponse(request, "food-opnion.html", { "food_opnion": None, "name": name, "id": id })

print("XXXXXXXXXXXXXXXX")
print("Adicionar estatistica quando não logado")
print("Portabilidade")
