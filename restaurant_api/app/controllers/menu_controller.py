from io import BytesIO
from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.schemas.menu_schema import MenuCreate, MenuUpdate, MenuRead
from app.models.menu import Menu
from app.models.menu_item import MenuItem
from app.models.dish import Dish
from app.models.ingredient import Ingredient
from app.models.dish_ingredient import DishIngredient
from app.utils.printing import menu_to_docx_bytes, menu_to_xlsx_bytes


ALLOWED_EXPORT_ROLE_IDS = {1, 2}


def create_menu(data: MenuCreate, db: Session) -> MenuRead:
    """
    Создаёт новое меню с указанным названием и списком блюд.

    Args:
        data (MenuCreate): Данные для создания меню, включая название и список ID блюд.
        db (Session): Сессия базы данных.

    Returns:
        MenuRead: Созданное меню с заполненными полями.

    Raises:
        HTTPException (404): Если какое-либо из указанных блюд не найдено.
    """
    menu = Menu(name=data.name)
    db.add(menu)
    db.commit()
    db.refresh(menu)

    for dish_id in data.dish_ids:
        dish = db.query(Dish).filter(Dish.id == dish_id).first()
        if not dish:
            raise HTTPException(status_code=404, detail=f"Блюдо с ID {dish_id} не найдено")
        db.add(MenuItem(menu_id=menu.id, dish_id=dish_id))

    db.commit()
    db.refresh(menu)

    item_ids = [item.dish_id for item in menu.items]
    return MenuRead(id=menu.id, name=menu.name, items=item_ids)


def get_all_menus(db: Session) -> List[MenuRead]:
    """
    Возвращает список всех меню.

    Args:
        db (Session): Сессия базы данных.

    Returns:
        List[MenuRead]: Список всех меню с их блюдами.
    """
    menus = db.query(Menu).all()
    return [
        MenuRead(
            id=menu.id,
            name=menu.name,
            item_ids = [item.dish_id for item in menu.items if item.dish_id is not None]
        )
        for menu in menus
    ]


def get_menu_by_id(menu_id: int, db: Session) -> MenuRead:
    """
    Возвращает меню по его ID.

    Args:
        menu_id (int): Идентификатор меню.
        db (Session): Сессия базы данных.

    Returns:
        MenuRead: Найденное меню.

    Raises:
        HTTPException (404): Если меню с указанным ID не найдено.
    """
    menu = db.query(Menu).filter(Menu.id == menu_id).first()
    if not menu:
        raise HTTPException(status_code=404, detail="Меню не найдено")
    item_ids = [item.dish_id for item in menu.items]
    return MenuRead(id=menu.id, name=menu.name, items=item_ids)


def update_menu(menu_id: int, data: MenuUpdate, db: Session) -> MenuRead:
    """
    Обновляет существующее меню: название и/или список блюд.

    Args:
        menu_id (int): Идентификатор обновляемого меню.
        data (MenuUpdate): Новые данные меню.
        db (Session): Сессия базы данных.

    Returns:
        MenuRead: Обновлённое меню.

    Raises:
        HTTPException (404): Если меню не найдено или указано несуществующее блюдо.
    """
    menu = db.query(Menu).filter(Menu.id == menu_id).first()
    if not menu:
        raise HTTPException(status_code=404, detail="Меню не найдено")

    if data.name is not None:
        menu.name = data.name

    if data.dish_ids is not None:
        db.query(MenuItem).filter(MenuItem.menu_id == menu_id).delete()
        for dish_id in data.dish_ids:
            dish = db.query(Dish).filter(Dish.id == dish_id).first()
            if not dish:
                raise HTTPException(status_code=404, detail=f"Блюдо с ID {dish_id} не найдено")
            db.add(MenuItem(menu_id=menu.id, dish_id=dish_id))

    db.commit()
    db.refresh(menu)

    item_ids = [item.dish_id for item in menu.items]
    return MenuRead(id=menu.id, name=menu.name, items=item_ids)


def delete_menu(menu_id: int, db: Session) -> dict[str, str]:
    """
    Удаляет меню и все связанные с ним элементы.

    Args:
        menu_id (int): Идентификатор удаляемого меню.
        db (Session): Сессия базы данных.

    Returns:
        dict[str, str]: Статус операции.

    Raises:
        HTTPException (404): Если меню не найдено.
    """
    menu = db.query(Menu).filter(Menu.id == menu_id).first()
    if not menu:
        raise HTTPException(status_code=404, detail="Меню не найдено")

    db.query(MenuItem).filter(MenuItem.menu_id == menu_id).delete()
    db.delete(menu)
    db.commit()
    return {"status": "deleted"}


def _fetch_dishes_with_ingredients(menu_id: int, db: Session) -> list[dict]:
    """
    Внутренняя функция: получает список блюд меню с полной информацией и ингредиентами.

    Args:
        menu_id (int): Идентификатор меню.
        db (Session): Сессия базы данных.

    Returns:
        list[dict]: Список словарей с данными о блюдах и их ингредиентах.
    """
    items = db.query(MenuItem).filter(MenuItem.menu_id == menu_id).all()
    dishes_data = []
    for mi in items:
        dish = db.query(Dish).filter(Dish.id == mi.dish_id).first()
        if not dish:
            continue
        ing_links = db.query(DishIngredient).filter(DishIngredient.dish_id == dish.id).all()
        ing_names = []
        for il in ing_links:
            ingredient = db.query(Ingredient).filter(Ingredient.id == il.ingredient_id).first()
            if ingredient:
                ing_names.append(ingredient.name)
        dishes_data.append({
            "id": dish.id,
            "name": dish.name,
            "description": dish.description,
            "price": dish.price,
            "ingredients": ing_names
        })
    return dishes_data


def export_menu_to_docx(menu_id: int, user_role_id: int, db: Session) -> BytesIO:
    """
    Экспортирует меню в формат DOCX.

    Args:
        menu_id (int): Идентификатор меню.
        user_role_id (int): Идентификатор роли пользователя.
        db (Session): Сессия базы данных.

    Returns:
        BytesIO: Байтовый поток файла DOCX.

    Raises:
        HTTPException (403): Если у пользователя недостаточно прав.
        HTTPException (404): Если меню не найдено.
    """
    if user_role_id not in ALLOWED_EXPORT_ROLE_IDS:
        raise HTTPException(status_code=403, detail="Доступ запрещён")

    menu = db.query(Menu).filter(Menu.id == menu_id).first()
    if not menu:
        raise HTTPException(status_code=404, detail="Меню не найдено")

    dishes_data = _fetch_dishes_with_ingredients(menu_id, db)
    file_bytes = menu_to_docx_bytes(menu, dishes_data)
    return BytesIO(file_bytes)


def export_menu_to_xlsx(menu_id: int, user_role_id: int, db: Session) -> BytesIO:
    """
    Экспортирует меню в формат XLSX.

    Args:
        menu_id (int): Идентификатор меню.
        user_role_id (int): Идентификатор роли пользователя.
        db (Session): Сессия базы данных.

    Returns:
        BytesIO: Байтовый поток файла XLSX.

    Raises:
        HTTPException (403): Если у пользователя недостаточно прав.
        HTTPException (404): Если меню не найдено.
    """
    if user_role_id not in ALLOWED_EXPORT_ROLE_IDS:
        raise HTTPException(status_code=403, detail="Доступ запрещён")

    menu = db.query(Menu).filter(Menu.id == menu_id).first()
    if not menu:
        raise HTTPException(status_code=404, detail="Меню не найдено")

    dishes_data = _fetch_dishes_with_ingredients(menu_id, db)
    file_bytes = menu_to_xlsx_bytes(menu, dishes_data)
    return BytesIO(file_bytes)

def search_menus_by_name(query: str, db: Session) -> list[MenuRead]:
    """
    Выполняет поиск меню по подстроке в названии (регистронезависимо).

    Args:
        query (str): Строка для поиска в поле name.
        db (Session): Сессия базы данных SQLAlchemy.

    Returns:
        list[MenuRead]: Список меню, у которых название содержит указанную подстроку.
    """
    menus = db.query(Menu).filter(Menu.name.ilike(f"%{query}%")).all()
    return [
        MenuRead(
            id=menu.id,
            name=menu.name,
            items=[item.dish_id for item in menu.items]
        )
        for menu in menus
    ]