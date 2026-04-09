import subprocess
import json
from models import Run, Menu, current_week
from sqlmodel import Session, select, func
from datetime import datetime, timedelta, date

def run_bandex(engine):
    dt = date.today()
    monday = dt - timedelta(days=dt.weekday())

    with Session(engine) as session:
        statement = select(func.count(Run.id)).where(Run.runned_at_week == monday)
        results = session.exec(statement)
        if results.one() != 0:
            return

    print("Novos cardápios foram criados")

    result = subprocess.run(["./bandex", "--format", "json", "-jae"], capture_output=True, text=True)
    result = json.loads(result.stdout)

    if not isinstance(result, list):
        return

    run = Run()
    menus = []

    for menu_info in result:
        menu_date = dt + timedelta(days=int(menu_info['weekday'])-4)
        menu = Menu(
            restaurant_id=menu_info['restaurant_id'],
            restaurant_name=menu_info['restaurant_name'],
            weekday=menu_info['weekday'],
            date=menu_date,
            menu_type=menu_info['menu_type'],
            state=menu_info['state'],
            calorific_value=menu_info['menu']['calorific_value'],
            content=menu_info['menu']['content'],
            observation=menu_info['menu']['observation']
        )
        menus.append(menu)

    with Session(engine) as session:
        session.add(run)
        session.commit()
        session.refresh(run)
        for menu in menus:
            menu.run_id = run.id
        session.add_all(menus)
        session.commit()

