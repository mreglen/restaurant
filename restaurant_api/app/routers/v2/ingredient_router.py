from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.schemas.v2.ingredient_schema import IngredientCreate, IngredientRead, IngredientUpdate
from app.controllers.v2.ingredient_controller import (
    create_ingredient,
    get_all_ingredients,
    get_ingredient_by_id,
    search_ingredients_by_name,
    update_ingredient,
    delete_ingredient,
)
from app.core.database import get_db
from app.dependencies.auth_deps import get_current_user, require_roles

router = APIRouter(prefix="/ingredients", tags=["Ingredients"])

"""Роли которым предоставлен доступ"""
ADMIN_ROLE_ID = 1
MANAGER_ROLE_ID = 2
MANAGER_AND_ADMIN = [MANAGER_ROLE_ID, ADMIN_ROLE_ID]


@router.post(
    "/",
    response_model=IngredientRead,
    dependencies=[Depends(require_roles(MANAGER_AND_ADMIN))]
)
def create_ingredient_endpoint(data: IngredientCreate, db: Session = Depends(get_db)):
    """
    Создаёт новый ингредиент. Доступно пользователям с ролью 'manager' (ID=2) или 'admin' (ID=1).
    """
    return create_ingredient(data, db)


@router.get(
    "/",
    response_model=list[IngredientRead]
)
def get_all_ingredients_endpoint(db: Session = Depends(get_db)):
    """
    Возвращает список всех ингредиентов. Доступно всем (публичный эндпоинт).
    """
    return get_all_ingredients(db)


@router.get(
    "/{ingredient_id}",
    response_model=IngredientRead
)
def get_ingredient_endpoint(ingredient_id: int, db: Session = Depends(get_db)):
    """
    Возвращает данные ингредиента по ID. Доступно всем (публичный эндпоинт).
    """
    return get_ingredient_by_id(ingredient_id, db)


@router.put(
    "/{ingredient_id}",
    response_model=IngredientRead,
    dependencies=[Depends(require_roles(MANAGER_AND_ADMIN))]
)
def update_ingredient_endpoint(ingredient_id: int, data: IngredientUpdate, db: Session = Depends(get_db)):
    """
    Обновляет название ингредиента. Доступно пользователям с ролью 'manager' или 'admin'.
    """
    return update_ingredient(ingredient_id, data, db)


@router.delete(
    "/{ingredient_id}",
    dependencies=[Depends(require_roles(MANAGER_AND_ADMIN))]
)
def delete_ingredient_endpoint(ingredient_id: int, db: Session = Depends(get_db)):
    """
    Удаляет ингредиент и все его связи с блюдами. Доступно пользователям с ролью 'manager' или 'admin'.
    """
    return delete_ingredient(ingredient_id, db)

@router.get(
    "/search/", 
    response_model=list[IngredientRead], 
    dependencies=[Depends(require_roles(MANAGER_AND_ADMIN))])
def search_ingredients(
    q: str = Query(..., min_length=1, description="Подстрока для поиска в названии ингредиента"),
    db: Session = Depends(get_db)
):
    """
    Выполняет поиск ингредиентов по части названия (регистронезависимо).

    - **q**: Часть названия ингредиента (минимум 1 символ).
    """
    return search_ingredients_by_name(q, db)