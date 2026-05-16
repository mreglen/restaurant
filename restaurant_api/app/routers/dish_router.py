from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.schemas.dish_schema import DishCreate, DishRead, DishUpdate
from app.controllers.dish_controller import (
    create_dish,
    delete_dish,
    get_all_dishes,
    get_dish_by_id,
    search_dishes_by_name,
    update_dish,
)
from app.core.database import get_db
from app.dependencies.auth_deps import get_current_user, require_roles

router = APIRouter(prefix="/dishes", tags=["Dishes"])

"""Роли которым предоставлен доступ"""
MANAGER_AND_ADMIN_ROLE_IDS = [1, 2]


@router.post(
    "/",
    response_model=DishRead,
    dependencies=[Depends(require_roles(MANAGER_AND_ADMIN_ROLE_IDS))]
)
def create_dish_endpoint(data: DishCreate, db: Session = Depends(get_db)):
    """
    Создаёт новое блюдо. Доступно пользователям с ролью manager (ID=2) или admin (ID=1).
    """
    return create_dish(data, db)


@router.get(
    "/",
    response_model=list[DishRead],
    dependencies=[Depends(get_current_user)]
)
def get_all_dishes_endpoint(db: Session = Depends(get_db)):
    """
    Возвращает список всех блюд. Доступно всем авторизованным пользователям.
    """
    return get_all_dishes(db)


@router.get(
    "/{dish_id}",
    response_model=DishRead,
    dependencies=[Depends(get_current_user)]
)
def get_dish_endpoint(dish_id: int, db: Session = Depends(get_db)):
    """
    Возвращает данные блюда по ID. Доступно всем авторизованным пользователям.
    """
    return get_dish_by_id(dish_id, db)


@router.put(
    "/{dish_id}",
    response_model=DishRead,
    dependencies=[Depends(require_roles(MANAGER_AND_ADMIN_ROLE_IDS))]
)
def update_dish_endpoint(dish_id: int, data: DishUpdate, db: Session = Depends(get_db)):
    """
    Обновляет данные блюда и его ингредиенты. Доступно пользователям с ролью manager или admin.
    """
    return update_dish(dish_id, data, db)

@router.delete(
    "/{dish_id}",
    dependencies=[Depends(require_roles(MANAGER_AND_ADMIN_ROLE_IDS))]
)
def delete_dish_endpoint(dish_id: int, db: Session = Depends(get_db)):
    """
    Удаляет блюдо и все его связи с ингредиентами. Доступно пользователям с ролью 'manager' или 'admin'.
    """
    return delete_dish(dish_id, db)

@router.get("/search/", response_model=list[DishRead], dependencies=[Depends(get_current_user)])
def search_dishes(
    q: str = Query(..., min_length=1, description="Подстрока для поиска в названии блюда"),
    db: Session = Depends(get_db)
):
    """
    Выполняет поиск блюд по части названия (регистронезависимо).

    - **q**: Часть названия блюда (минимум 1 символ).
    """
    return search_dishes_by_name(q, db)