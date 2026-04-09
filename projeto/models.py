from typing import List, Optional
from datetime import datetime, timedelta, date
from sqlmodel import Field, Relationship, SQLModel

def current_week():
    dt = date.today()
    monday = dt - timedelta(days=dt.weekday())
    return monday

class Run(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    runned_at: datetime = Field(default_factory=datetime.now)
    runned_at_week: date = Field(default_factory=current_week, index=True)

    menus: List["Menu"] = Relationship(back_populates="run")

class Menu(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    restaurant_id: int # Id do restaurante;
    restaurant_name: str # Nome do restaurante;
    weekday: int # Dia da semana da refeição (Domingo: 1, Segunda: 2, …, Sabado: 7);
    date: date # Dia da refeição
    menu_type: str # "Almoço" ou "Jantar"" dependendo do tipo da refeição;
    state: str # "opened" ou "closed" dependendo se o restaurante esta fechado;
    calorific_value: int | None # Valor Calórico da refeição (None se não há informações sobre o valor energético);
    content: str # O conteúdo da refeição;
    observation: str # As observações do refeição.
    run_id: int = Field(foreign_key="run.id")

    run: Optional["Run"] = Relationship(back_populates="menus")


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    login: str
    food_opnions: List["FoodOpnion"] = Relationship(back_populates="owner")


class FoodOpnion(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    food_name: str
    liked: bool
    owner_id: int = Field(foreign_key="user.id")

    owner: Optional["User"] = Relationship(back_populates="food_opnions")

