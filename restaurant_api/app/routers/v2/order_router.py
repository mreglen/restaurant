from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.schemas.v2.order_schema import OrderCreate, OrderRead, OrderUpdate
from app.controllers.v2.order_controller import (
    create_order,
    get_all_orders,
    get_order_by_id,
    update_order,
    delete_order,
)
from app.core.database import get_db
from app.dependencies.auth_deps import get_current_user, require_roles

router = APIRouter(prefix="/orders", tags=["Orders"])

"""Роли которым предоставлен доступ"""
ADMIN_ROLE_ID = 1
MANAGER_ROLE_ID = 2
MANAGER_AND_ADMIN = [MANAGER_ROLE_ID, ADMIN_ROLE_ID]


@router.post(
    "/",
    response_model=OrderRead,
    dependencies=[Depends(get_current_user)]
)
def create_order_endpoint(data: OrderCreate, db: Session = Depends(get_db)):
    """
    Создаёт новый заказ. Доступно всем авторизованным пользователям (например, официантам).
    """
    return create_order(data, db)


@router.get(
    "/",
    response_model=list[OrderRead],
    dependencies=[Depends(get_current_user)]
)
def get_all_orders_endpoint(db: Session = Depends(get_db)):
    """
    Возвращает список всех заказов. Доступно всем авторизованным пользователям.
    """
    return get_all_orders(db)


@router.get(
    "/{order_id}",
    response_model=OrderRead,
    dependencies=[Depends(get_current_user)]
)
def get_order_endpoint(order_id: int, db: Session = Depends(get_db)):
    """
    Возвращает данные заказа по ID. Доступно всем авторизованным пользователям.
    """
    return get_order_by_id(order_id, db)


@router.put(
    "/{order_id}",
    response_model=OrderRead,
    dependencies=[Depends(require_roles(MANAGER_AND_ADMIN))]
)
def update_order_endpoint(order_id: int, data: OrderUpdate, db: Session = Depends(get_db)):
    """
    Обновляет данные заказа (номер стола, клиент). Доступно пользователям с ролью 'manager' (ID=2) или 'admin' (ID=1).
    """
    return update_order(order_id, data, db)


@router.delete(
    "/{order_id}",
    dependencies=[Depends(require_roles(MANAGER_AND_ADMIN))]
)
def delete_order_endpoint(order_id: int, db: Session = Depends(get_db)):
    """
    Удаляет заказ и все его позиции. Доступно пользователям с ролью 'manager' или 'admin'.
    """
    return delete_order(order_id, db)

