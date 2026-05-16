#!/usr/bin/env python
"""
Добавляет блюда в меню основной БД (таблица menu_items).
Запуск: python scripts/populate_menu_dishes.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.core.database import SessionLocal
from app.models.client import Client  # noqa: F401
from app.models.dish import Dish
from app.models.dish_ingredient import DishIngredient  # noqa: F401
from app.models.employee import Employee  # noqa: F401
from app.models.ingredient import Ingredient  # noqa: F401
from app.models.menu import Menu
from app.models.menu_item import MenuItem
from app.models.order import Order  # noqa: F401
from app.models.order_item import OrderItem  # noqa: F401
from app.models.role import Role  # noqa: F401
from app.models.table_assignment import TableAssignment  # noqa: F401


def populate() -> None:
    db = SessionLocal()
    try:
        menus = db.query(Menu).order_by(Menu.id).all()
        dishes = db.query(Dish).order_by(Dish.id).all()
        if not dishes:
            print('Нет блюд в БД. Сначала: python scripts/seed_database.py')
            return
        if not menus:
            print('Нет меню в БД. Сначала: python scripts/seed_database.py')
            return

        # Распределение блюд по меню (по имени или по порядку)
        plan: dict[str, list[int]] = {}
        dish_ids = [d.id for d in dishes]
        by_name = {m.name.lower(): m for m in menus}

        if 'основное меню' in by_name or len(menus) >= 1:
            key_menu = by_name.get('основное меню') or menus[0]
            plan[key_menu.id] = dish_ids[:4] if len(dish_ids) >= 4 else dish_ids[:]

        if 'бизнес-ланч' in by_name:
            m = by_name['бизнес-ланч']
            plan[m.id] = [dish_ids[2], dish_ids[4]] if len(dish_ids) > 4 else dish_ids[1:3]
        elif len(menus) >= 2:
            plan[menus[1].id] = dish_ids[2:5] if len(dish_ids) > 2 else dish_ids

        if 'десерты и напитки' in by_name:
            m = by_name['десерты и напитки']
            plan[m.id] = [dish_ids[-1]] if dish_ids else []
        elif len(menus) >= 3:
            plan[menus[2].id] = [dish_ids[-1]] if dish_ids else []

        # Меню без плана — все блюда
        for m in menus:
            if m.id not in plan:
                plan[m.id] = dish_ids

        added = 0
        for m in menus:
            # Пустые меню — все блюда; «Основное» — полный каталог
            target_ids = plan.get(m.id, dish_ids)
            if db.query(MenuItem).filter(MenuItem.menu_id == m.id).count() == 0:
                target_ids = dish_ids
            elif 'основн' in m.name.lower():
                target_ids = dish_ids

            existing = {
                row.dish_id
                for row in db.query(MenuItem).filter(MenuItem.menu_id == m.id).all()
            }
            for dish_id in target_ids:
                if dish_id not in existing:
                    db.add(MenuItem(menu_id=m.id, dish_id=dish_id))
                    added += 1

        db.commit()
        for m in menus:
            count = db.query(MenuItem).filter(MenuItem.menu_id == m.id).count()
            print(f'  {m.name}: {count} блюд(а)')
        print(f'Добавлено связей: {added}')
    finally:
        db.close()


if __name__ == '__main__':
    populate()
