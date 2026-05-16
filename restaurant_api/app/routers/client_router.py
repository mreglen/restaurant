from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.schemas.client_schema import ClientCreate, ClientRead, ClientUpdate
from app.controllers.client_controller import (
    create_client,
    get_all_clients,
    get_client_by_id,
    search_clients_by_name,
    update_client,
    delete_client,
)
from app.core.database import get_db
from app.dependencies.auth_deps import get_current_user, require_roles

router = APIRouter(prefix="/clients", tags=["Clients"])

"""Роли которым предоставлен доступ"""
MANAGER_AND_ADMIN_ROLE_IDS = [1, 2]


@router.post(
    "/",
    response_model=ClientRead,
    dependencies=[Depends(require_roles(MANAGER_AND_ADMIN_ROLE_IDS))]
)
def create_client_endpoint(data: ClientCreate, db: Session = Depends(get_db)):
    """
    Создаёт нового клиента. Доступно пользователям с ролью manager (ID=2) или admin (ID=1).
    """
    return create_client(data, db)


@router.get(
    "/",
    response_model=list[ClientRead],
    dependencies=[Depends(get_current_user)]
)
def get_all_clients_endpoint(db: Session = Depends(get_db)):
    """
    Возвращает список всех клиентов. Доступно всем авторизованным пользователям.
    """
    return get_all_clients(db)


@router.get(
    "/{client_id}",
    response_model=ClientRead,
    dependencies=[Depends(get_current_user)]
)
def get_client_endpoint(client_id: int, db: Session = Depends(get_db)):
    """
    Возвращает данные клиента по ID. Доступно всем авторизованным пользователям.
    """
    return get_client_by_id(client_id, db)



@router.put(
    "/{client_id}",
    response_model=ClientRead,
    dependencies=[Depends(require_roles(MANAGER_AND_ADMIN_ROLE_IDS))]
)
def update_client_endpoint(client_id: int, data: ClientUpdate, db: Session = Depends(get_db)):
    """
    Обновляет данные клиента по ID. Доступно пользователям с ролью manager или admin.
    """
    return update_client(client_id, data, db)


@router.delete(
    "/{client_id}",
    dependencies=[Depends(require_roles(MANAGER_AND_ADMIN_ROLE_IDS))]
)
def delete_client_endpoint(client_id: int, db: Session = Depends(get_db)):
    """
    Удаляет клиента по ID. Доступно пользователям с ролью manager или admin.
    """
    return delete_client(client_id, db)


@router.get("/search/", response_model=List[ClientRead], dependencies=[Depends(get_current_user)])
def search_clients(
    q: str = Query(..., min_length=1, description="Подстрока для поиска в ФИО клиента"),
    db: Session = Depends(get_db)
):
    """
    Выполняет поиск клиентов по подстроке в поле full_name (регистронезависимо).

    - **q**: Часть имени, фамилии или отчества (минимум 1 символ).
    """
    return search_clients_by_name(q, db)