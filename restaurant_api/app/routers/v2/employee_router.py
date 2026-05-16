from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.schemas.v2.employee_schema import EmployeeCreate, EmployeeRead, EmployeeUpdate
from app.controllers.v2.employee_controller import (
    create_employee,
    get_all_employees,
    get_employee_by_id,
    search_employees_by_name,
    update_employee,
    delete_employee,
)
from app.core.database import get_db
from app.dependencies.auth_deps import require_roles

router = APIRouter(prefix="/employees", tags=["Employees"])

"""Роли которым предоставлен доступ"""
ADMIN_ROLE_ID = 1
MANAGER_ROLE_ID = 2
ADMIN_ONLY = [ADMIN_ROLE_ID]
MANAGER_AND_ADMIN = [MANAGER_ROLE_ID, ADMIN_ROLE_ID]


@router.post(
    "/",
    response_model=EmployeeRead,
    dependencies=[Depends(require_roles(ADMIN_ONLY))]
)
def create_employee_endpoint(data: EmployeeCreate, db: Session = Depends(get_db)):
    """
    Создаёт нового сотрудника. Доступно только пользователям с ролью 'admin' (ID=1).
    """
    return create_employee(data, db)


@router.get(
    "/",
    response_model=list[EmployeeRead],
    dependencies=[Depends(require_roles(MANAGER_AND_ADMIN))]
)
def get_all_employees_endpoint(db: Session = Depends(get_db)):
    """
    Возвращает список всех сотрудников. Доступно пользователям с ролями 'manager' (ID=2) или 'admin' (ID=1).
    """
    return get_all_employees(db)


# BUG-003 FIX: Маршрут /search/ должен быть ДО /{employee_id}
@router.get("/search/", response_model=list[EmployeeRead], dependencies=[Depends(require_roles(MANAGER_AND_ADMIN))])
def search_employees(
    q: str = Query(..., min_length=1, description="Подстрока для поиска в ФИО сотрудника"),
    db: Session = Depends(get_db)
):
    """
    Выполняет поиск сотрудников по части ФИО (регистронезависимо).

    - **q**: Часть имени, фамилии или отчества (минимум 1 символ).
    """
    return search_employees_by_name(q, db)


@router.get(
    "/{employee_id}",
    response_model=EmployeeRead,
    dependencies=[Depends(require_roles(MANAGER_AND_ADMIN))]
)
def get_employee_endpoint(employee_id: int, db: Session = Depends(get_db)):
    """
    Возвращает данные сотрудника по ID. Доступно пользователям с ролями 'manager' или 'admin'.
    """
    return get_employee_by_id(employee_id, db)


@router.put(
    "/{employee_id}",
    response_model=EmployeeRead,
    dependencies=[Depends(require_roles(ADMIN_ONLY))]
)
def update_employee_endpoint(employee_id: int, data: EmployeeUpdate, db: Session = Depends(get_db)):
    """
    Обновляет данные сотрудника (кроме логина и пароля). Доступно только пользователям с ролью 'admin'.
    """
    return update_employee(employee_id, data, db)


@router.delete(
    "/{employee_id}",
    dependencies=[Depends(require_roles(ADMIN_ONLY))]
)
def delete_employee_endpoint(employee_id: int, db: Session = Depends(get_db)):
    """
    Удаляет сотрудника по ID. Доступно только пользователям с ролью 'admin'.
    """
    return delete_employee(employee_id, db)