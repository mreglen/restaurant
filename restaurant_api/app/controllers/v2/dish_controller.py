from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.schemas.dish_schema import DishCreate, DishUpdate, DishRead
from app.models.dish import Dish
from app.models.ingredient import Ingredient
from app.models.dish_ingredient import DishIngredient


def create_dish(data: DishCreate, db: Session) -> DishRead:
    """
    Создаёт новое блюдо с указанными ингредиентами.

    Args:
        data (DishCreate): Данные для создания блюда: название, описание, цена и список ID ингредиентов.
        db (Session): Сессия базы данных SQLAlchemy.

    Returns:
        DishRead: Созданное блюдо с полным списком ID ингредиентов.

    Raises:
        HTTPException: Если какой-либо из указанных ингредиентов не найден (404).
    """
    dish = Dish(
        name=data.name,
        description=data.description,
        price=data.price
    )
    db.add(dish)
    db.commit()
    db.refresh(dish)

 
    for ing_id in data.ingredient_ids:
        ingredient = db.query(Ingredient).filter(Ingredient.id == ing_id).first()
        if not ingredient:
            raise HTTPException(status_code=404, detail=f"Ингредиент с идентификатором {ing_id} не найден")
        db.add(DishIngredient(dish_id=dish.id, ingredient_id=ing_id))

    db.commit()
    db.refresh(dish)

    ingredient_ids = [di.ingredient_id for di in dish.ingredients]
    return DishRead(
        id=dish.id,
        name=dish.name,
        description=dish.description,
        price=dish.price,
        ingredients=ingredient_ids
    )


def get_all_dishes(db: Session) -> list[DishRead]:
    """
    Возвращает список всех блюд с их ингредиентами.

    Args:
        db (Session): Сессия базы данных SQLAlchemy.

    Returns:
        list[DishRead]: Список всех блюд.
    """
    dishes = db.query(Dish).all()
    result = []
    for dish in dishes:
        ingredient_ids = [di.ingredient_id for di in dish.ingredients]
        result.append(
            DishRead(
                id=dish.id,
                name=dish.name,
                description=dish.description,
                price=dish.price,
                ingredients=ingredient_ids
            )
        )
    return result


def get_dish_by_id(dish_id: int, db: Session) -> DishRead:
    """
    Получает блюдо по его уникальному идентификатору.

    Args:
        dish_id (int): ID блюда.
        db (Session): Сессия базы данных SQLAlchemy.

    Returns:
        DishRead: Найденное блюдо с ингредиентами.

    Raises:
        HTTPException: Если блюдо не найдено (404).
    """
    dish = db.query(Dish).filter(Dish.id == dish_id).first()
    if not dish:
        raise HTTPException(status_code=404, detail="Блюдо не найдено")

    ingredient_ids = [di.ingredient_id for di in dish.ingredients]
    return DishRead(
        id=dish.id,
        name=dish.name,
        description=dish.description,
        price=dish.price,
        ingredients=ingredient_ids
    )

def search_dishes_by_name(query: str, db: Session) -> list[DishRead]:
    """
    Выполняет поиск блюд по подстроке в названии (регистронезависимо).

    Args:
        query (str): Строка для поиска в поле name.
        db (Session): Сессия базы данных SQLAlchemy.

    Returns:
        list[DishRead]: Список блюд, у которых название содержит указанную подстроку.
    """
    dishes = db.query(Dish).filter(Dish.name.ilike(f"%{query}%")).all()
    result = []
    for dish in dishes:
        ingredient_ids = [di.ingredient_id for di in dish.ingredients]
        result.append(
            DishRead(
                id=dish.id,
                name=dish.name,
                description=dish.description,
                price=dish.price,
                ingredients=ingredient_ids
            )
        )
    return result

def update_dish(dish_id: int, data: DishUpdate, db: Session) -> DishRead:
    """
    Обновляет данные блюда и его список ингредиентов.

    Args:
        dish_id (int): ID обновляемого блюда.
        data (DishUpdate): Обновлённые данные блюда (опциональные поля).
        db (Session): Сессия базы данных SQLAlchemy.

    Returns:
        DishRead: Обновлённое блюдо с актуальным списком ингредиентов.

    Raises:
        HTTPException: Если блюдо не найдено (404) или указан несуществующий ингредиент (404).
    """
    dish = db.query(Dish).filter(Dish.id == dish_id).first()
    if not dish:
        raise HTTPException(status_code=404, detail="Блюдо не найдено")

    if data.name is not None:
        dish.name = data.name
    if data.description is not None:
        dish.description = data.description
    if data.price is not None:
        dish.price = data.price

    if data.ingredient_ids is not None:
       
        db.query(DishIngredient).filter(DishIngredient.dish_id == dish_id).delete()

        
        for ing_id in data.ingredient_ids:
            ingredient = db.query(Ingredient).filter(Ingredient.id == ing_id).first()
            if not ingredient:
                raise HTTPException(status_code=404, detail=f"Ингредиент с идентификатором {ing_id} не найден")
            db.add(DishIngredient(dish_id=dish.id, ingredient_id=ing_id))

    db.commit()
    db.refresh(dish)

    ingredient_ids = [di.ingredient_id for di in dish.ingredients]
    return DishRead(
        id=dish.id,
        name=dish.name,
        description=dish.description,
        price=dish.price,
        ingredients=ingredient_ids
    )

def delete_dish(dish_id: int, db: Session) -> dict[str, str]:
    """
    Удаляет блюдо и все его связи с ингредиентами.

    Args:
        dish_id (int): ID удаляемого блюда.
        db (Session): Сессия базы данных SQLAlchemy.

    Returns:
        dict[str, str]: Подтверждение удаления: {"status": "deleted"}.

    Raises:
        HTTPException: Если блюдо не найдено (404).
    """
    dish = db.query(Dish).filter(Dish.id == dish_id).first()
    if not dish:
        raise HTTPException(status_code=404, detail="Блюдо не найдено")

  
    db.query(DishIngredient).filter(DishIngredient.dish_id == dish_id).delete()

    db.delete(dish)
    db.commit()
    return {"status": "deleted"}