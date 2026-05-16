from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.schemas.ingredient_schema import IngredientCreate, IngredientUpdate, IngredientRead
from app.models.ingredient import Ingredient
from app.models.dish_ingredient import DishIngredient


def create_ingredient(data: IngredientCreate, db: Session) -> IngredientRead:
    """
    Создаёт новый ингредиент.

    Args:
        data (IngredientCreate): Данные для создания ингредиента: название.
        db (Session): Сессия базы данных SQLAlchemy.

    Returns:
        IngredientRead: Созданный ингредиент с присвоенным ID.
    """
    ingredient = Ingredient(name=data.name)
    db.add(ingredient)
    db.commit()
    db.refresh(ingredient)
    return ingredient


def get_all_ingredients(db: Session) -> list[IngredientRead]:
    """
    Возвращает список всех ингредиентов.

    Args:
        db (Session): Сессия базы данных SQLAlchemy.

    Returns:
        list[IngredientRead]: Список всех ингредиентов в системе.
    """
    return db.query(Ingredient).all()


def get_ingredient_by_id(ingredient_id: int, db: Session) -> IngredientRead:
    """
    Получает ингредиент по его уникальному идентификатору.

    Args:
        ingredient_id (int): ID ингредиента.
        db (Session): Сессия базы данных SQLAlchemy.

    Returns:
        IngredientRead: Найденный ингредиент.

    Raises:
        HTTPException: Если ингредиент с указанным ID не найден (404).
    """
    ingredient = db.query(Ingredient).filter(Ingredient.id == ingredient_id).first()
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ингредиент не найден")
    return ingredient


def update_ingredient(ingredient_id: int, data: IngredientUpdate, db: Session) -> IngredientRead:
    """
    Обновляет название ингредиента.

    Args:
        ingredient_id (int): ID обновляемого ингредиента.
        data (IngredientUpdate): Новое название ингредиента (опционально).
        db (Session): Сессия базы данных SQLAlchemy.

    Returns:
        IngredientRead: Обновлённый ингредиент.

    Raises:
        HTTPException: Если ингредиент с указанным ID не найден (404).
    """
    ingredient = db.query(Ingredient).filter(Ingredient.id == ingredient_id).first()
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ингредиент не найден")

    if data.name is not None:
        ingredient.name = data.name

    db.commit()
    db.refresh(ingredient)
    return ingredient


def delete_ingredient(ingredient_id: int, db: Session) -> dict[str, str]:
    """
    Удаляет ингредиент и все связанные с ним записи в промежуточной таблице DishIngredient.

    Args:
        ingredient_id (int): ID удаляемого ингредиента.
        db (Session): Сессия базы данных SQLAlchemy.

    Returns:
        dict[str, str]: Подтверждение удаления: {"status": "deleted"}.

    Raises:
        HTTPException: Если ингредиент с указанным ID не найден (404).
    """
    ingredient = db.query(Ingredient).filter(Ingredient.id == ingredient_id).first()
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ингредиент не найден")


    db.query(DishIngredient).filter(DishIngredient.ingredient_id == ingredient_id).delete()

    db.delete(ingredient)
    db.commit()
    return {"status": "deleted"}

def search_ingredients_by_name(query: str, db: Session) -> list[IngredientRead]:
    """
    Выполняет поиск ингредиентов по подстроке в названии (регистронезависимо).

    Args:
        query (str): Строка для поиска в поле name.
        db (Session): Сессия базы данных SQLAlchemy.

    Returns:
        list[IngredientRead]: Список ингредиентов, у которых название содержит указанную подстроку.
    """
    ingredients = db.query(Ingredient).filter(Ingredient.name.ilike(f"%{query}%")).all()
    return ingredients