"""
Заполнение основной БД демонстрационными данными ресторана.
"""
from __future__ import annotations

import argparse

from sqlalchemy.orm import Session

from app.core.database import Base, SessionLocal, engine
from app.core.security import hash_password
from app.models.client import Client
from app.models.dish import Dish
from app.models.dish_ingredient import DishIngredient
from app.models.employee import Employee
from app.models.ingredient import Ingredient
from app.models.menu import Menu
from app.models.menu_item import MenuItem
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.role import Role
from app.models.table_assignment import TableAssignment


def clear_app_data(db: Session) -> None:
    """Удаляет данные приложения (не трогает таблицы Django)."""
    db.query(OrderItem).delete()
    db.query(Order).delete()
    db.query(MenuItem).delete()
    db.query(Menu).delete()
    db.query(DishIngredient).delete()
    db.query(Dish).delete()
    db.query(TableAssignment).delete()
    db.query(Employee).delete()
    db.query(Client).delete()
    db.query(Ingredient).delete()
    db.query(Role).delete()
    db.commit()


def seed(db: Session) -> None:
    role_admin = Role(name='admin', description='Администратор системы')
    role_manager = Role(name='manager', description='Менеджер зала')
    role_waiter = Role(name='waiter', description='Официант')
    db.add_all([role_admin, role_manager, role_waiter])
    db.flush()

    employees = [
        Employee(
            last_name='Иванов',
            first_name='Алексей',
            patronymic='Петрович',
            phone='+79001110001',
            username='admin',
            password_hash=hash_password('admin123'),
            role_id=role_admin.id,
        ),
        Employee(
            last_name='Петрова',
            first_name='Мария',
            patronymic='Сергеевна',
            phone='+79001110002',
            username='manager',
            password_hash=hash_password('manager123'),
            role_id=role_manager.id,
        ),
        Employee(
            last_name='Сидоров',
            first_name='Дмитрий',
            patronymic='',
            phone='+79001110003',
            username='waiter',
            password_hash=hash_password('waiter123'),
            role_id=role_waiter.id,
        ),
    ]
    db.add_all(employees)
    db.flush()

    ingredients = [
        Ingredient(name='Говядина'),
        Ingredient(name='Картофель'),
        Ingredient(name='Лук'),
        Ingredient(name='Сливки'),
        Ingredient(name='Лосось'),
        Ingredient(name='Салат'),
        Ingredient(name='Помидор'),
        Ingredient(name='Сыр моцарелла'),
    ]
    db.add_all(ingredients)
    db.flush()

    dishes = [
        Dish(
            name='Борщ украинский',
            description='Классический борщ со сметаной и зеленью',
            price=350.0,
        ),
        Dish(
            name='Стейк рибай',
            description='Говяжий стейк средней прожарки',
            price=1290.0,
        ),
        Dish(
            name='Салат Цезарь',
            description='С курицей, пармезаном и соусом цезарь',
            price=420.0,
        ),
        Dish(
            name='Лосось на гриле',
            description='Филе лосося с овощами',
            price=890.0,
        ),
        Dish(
            name='Паста карбонара',
            description='Спагетти с беконом и сливочным соусом',
            price=550.0,
        ),
        Dish(
            name='Тирамису',
            description='Итальянский десерт с маскарпоне',
            price=320.0,
        ),
    ]
    db.add_all(dishes)
    db.flush()

    links = [
        (dishes[0].id, ingredients[0].id),
        (dishes[0].id, ingredients[1].id),
        (dishes[0].id, ingredients[2].id),
        (dishes[1].id, ingredients[0].id),
        (dishes[2].id, ingredients[5].id),
        (dishes[2].id, ingredients[6].id),
        (dishes[3].id, ingredients[4].id),
        (dishes[4].id, ingredients[3].id),
    ]
    db.add_all([DishIngredient(dish_id=d, ingredient_id=i) for d, i in links])

    menus = [
        Menu(name='Основное меню'),
        Menu(name='Бизнес-ланч'),
        Menu(name='Десерты и напитки'),
    ]
    db.add_all(menus)
    db.flush()

    menu_links = [
        *((menus[0].id, d.id) for d in dishes),  # Основное меню — все блюда
        (menus[1].id, dishes[2].id),
        (menus[1].id, dishes[4].id),
        (menus[2].id, dishes[5].id),
    ]
    db.add_all([MenuItem(menu_id=m, dish_id=d) for m, d in menu_links])

    clients = [
        Client(
            last_name='Смирнов',
            first_name='Игорь',
            patronymic='Андреевич',
            phone='+79002220001',
            is_vip=True,
            bonus_points=150,
        ),
        Client(
            last_name='Козлова',
            first_name='Анна',
            patronymic='',
            phone='+79002220002',
            is_vip=False,
            bonus_points=40,
        ),
        Client(
            last_name='Волков',
            first_name='Пётр',
            patronymic='Николаевич',
            phone='+79002220003',
            is_vip=False,
            bonus_points=0,
        ),
    ]
    db.add_all(clients)
    db.flush()

    db.add_all([
        TableAssignment(table_number=1, employee_id=employees[2].id),
        TableAssignment(table_number=2, employee_id=employees[2].id),
        TableAssignment(table_number=3, employee_id=employees[1].id),
        TableAssignment(table_number=5, employee_id=employees[1].id),
    ])

    order1 = Order(client_id=clients[0].id, table_number=1, total_price=0)
    order2 = Order(client_id=clients[1].id, table_number=3, total_price=0)
    db.add_all([order1, order2])
    db.flush()

    items = [
        OrderItem(order_id=order1.id, dish_id=dishes[0].id, quantity=2, price=dishes[0].price),
        OrderItem(order_id=order1.id, dish_id=dishes[5].id, quantity=1, price=dishes[5].price),
        OrderItem(order_id=order2.id, dish_id=dishes[2].id, quantity=1, price=dishes[2].price),
        OrderItem(order_id=order2.id, dish_id=dishes[4].id, quantity=1, price=dishes[4].price),
    ]
    db.add_all(items)
    order1.total_price = sum(i.price * i.quantity for i in items if i.order_id == order1.id)
    order2.total_price = sum(i.price * i.quantity for i in items if i.order_id == order2.id)

    db.commit()


def run_seed(*, force: bool = False) -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        has_data = db.query(Role).count() > 0
        if has_data and not force:
            print('В базе уже есть данные. Запустите с --force для перезаписи.')
            return
        if force:
            clear_app_data(db)
        seed(db)
        print('База restaurant заполнена демо-данными.')
        print('Вход: admin / admin123  |  manager / manager123  |  waiter / waiter123')
    finally:
        db.close()


def main() -> None:
    parser = argparse.ArgumentParser(description='Заполнение БД restaurant демо-данными')
    parser.add_argument(
        '--force',
        action='store_true',
        help='Очистить данные приложения и заполнить заново',
    )
    args = parser.parse_args()
    run_seed(force=args.force)


if __name__ == '__main__':
    main()
