from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import List

from app.schemas.table_assignment_schema import TableAssignmentCreate, TableAssignmentRead
from app.models.table_assignment import TableAssignment
from app.models.employee import Employee

WAITER_ROLE_ID = 3


def assign_table_to_waiter(data: TableAssignmentCreate, db: Session) -> TableAssignmentRead:
    """
    Назначает официанта на стол.

    Args:
        data (TableAssignmentCreate): Номер стола и ID официанта.
        db (Session): Сессия базы данных SQLAlchemy.

    Returns:
        TableAssignmentRead: Созданное назначение.

    Raises:
        HTTPException:
            - 404, если сотрудник с указанным ID не найден.
            - 400, если сотрудник не является официантом.
    """
    employee = db.query(Employee).filter(Employee.id == data.employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Сотрудник не найден")

    if employee.role_id != WAITER_ROLE_ID:
        raise HTTPException(status_code=400, detail="Могут быть назначены только официанты to tables")

    assignment = TableAssignment(table_number=data.table_number, employee_id=data.employee_id)
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return assignment


def get_all_table_assignments(db: Session) -> List[TableAssignmentRead]:
    """
    Возвращает список всех назначений столов официантам.

    Args:
        db (Session): Сессия базы данных SQLAlchemy.

    Returns:
        list[TableAssignmentRead]: Список всех текущих назначений.
    """
    return db.query(TableAssignment).all()


def get_table_assignment_by_id(assignment_id: int, db: Session) -> TableAssignmentRead:
    """
    Получает назначение стола по его уникальному идентификатору.

    Args:
        assignment_id (int): ID назначения.
        db (Session): Сессия базы данных SQLAlchemy.

    Returns:
        TableAssignmentRead: Найденное назначение.

    Raises:
        HTTPException: 404, если назначение не найдено.
    """
    assignment = db.query(TableAssignment).filter(TableAssignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Задание не найдено")
    return assignment


def update_table_assignment(assignment_id: int, data: TableAssignmentCreate, db: Session) -> TableAssignmentRead:
    """
    Обновляет назначение стола: изменяет номер стола и/или официанта.

    Args:
        assignment_id (int): ID обновляемого назначения.
        data (TableAssignmentCreate): Новые данные: номер стола и ID официанта.
        db (Session): Сессия базы данных SQLAlchemy.

    Returns:
        TableAssignmentRead: Обновлённое назначение.

    Raises:
        HTTPException:
            - 404, если назначение или сотрудник не найдены.
            - 400, если указанный сотрудник не является официантом.
    """
    assignment = db.query(TableAssignment).filter(TableAssignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Задание не найдено")

    employee = db.query(Employee).filter(Employee.id == data.employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Сотрудник не найден")

    if employee.role_id != WAITER_ROLE_ID:
        raise HTTPException(status_code=400, detail="Могут быть назначены только официанты")

    assignment.table_number = data.table_number
    assignment.employee_id = data.employee_id

    db.commit()
    db.refresh(assignment)
    return assignment


def delete_table_assignment(assignment_id: int, db: Session) -> dict[str, str]:
    """
    Удаляет назначение стола.

    Args:
        assignment_id (int): ID удаляемого назначения.
        db (Session): Сессия базы данных SQLAlchemy.

    Returns:
        dict[str, str]: Подтверждение удаления: {"status": "deleted"}.

    Raises:
        HTTPException: 404, если назначение не найдено.
    """
    assignment = db.query(TableAssignment).filter(TableAssignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Задание не найдено")

    db.delete(assignment)
    db.commit()
    return {"status": "deleted"}