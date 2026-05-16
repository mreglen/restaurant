from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.schemas.table_assignment_schema import TableAssignmentCreate, TableAssignmentRead
from app.controllers.table_assignment_controller import (
    assign_table_to_waiter,
    get_all_table_assignments,
    get_table_assignment_by_id,
    update_table_assignment,
    delete_table_assignment,
)
from app.core.database import get_db
from app.dependencies.auth_deps import get_current_user, require_roles

router = APIRouter(prefix="/tables", tags=["Tables"])

"""Роли которым предоставлен доступ"""
ADMIN_ROLE_ID = 1
MANAGER_ROLE_ID = 2
MANAGER_AND_ADMIN = [MANAGER_ROLE_ID, ADMIN_ROLE_ID]


@router.post(
    "/",
    response_model=TableAssignmentRead,
    dependencies=[Depends(require_roles(MANAGER_AND_ADMIN))]
)
def assign_table_endpoint(data: TableAssignmentCreate, db: Session = Depends(get_db)):
    """
    Назначает официанта на стол. Доступно пользователям с ролью 'manager' (ID=2) или 'admin' (ID=1).
    """
    return assign_table_to_waiter(data, db)


@router.get(
    "/",
    response_model=list[TableAssignmentRead],
    dependencies=[Depends(get_current_user)]
)
def get_all_assignments_endpoint(db: Session = Depends(get_db)):
    """
    Возвращает список всех назначений столов. Доступно всем авторизованным пользователям.
    """
    return get_all_table_assignments(db)


@router.get(
    "/{assignment_id}",
    response_model=TableAssignmentRead,
    dependencies=[Depends(get_current_user)]
)
def get_assignment_endpoint(assignment_id: int, db: Session = Depends(get_db)):
    """
    Возвращает назначение по ID. Доступно всем авторизованным пользователям.
    """
    return get_table_assignment_by_id(assignment_id, db)


@router.put(
    "/{assignment_id}",
    response_model=TableAssignmentRead,
    dependencies=[Depends(require_roles(MANAGER_AND_ADMIN))]
)
def update_assignment_endpoint(
    assignment_id: int,
    data: TableAssignmentCreate,
    db: Session = Depends(get_db)
):
    """
    Обновляет назначение стола. Доступно пользователям с ролью 'manager' или 'admin'.
    """
    return update_table_assignment(assignment_id, data, db)


@router.delete(
    "/{assignment_id}",
    dependencies=[Depends(require_roles(MANAGER_AND_ADMIN))]
)
def delete_assignment_endpoint(assignment_id: int, db: Session = Depends(get_db)):
    """
    Удаляет назначение стола. Доступно пользователям с ролью 'manager' или 'admin'.
    """
    return delete_table_assignment(assignment_id, db)