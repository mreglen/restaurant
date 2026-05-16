from sqlalchemy import or_
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.schemas.employee_schema import EmployeeCreate, EmployeeUpdate, EmployeeRead
from app.models.employee import Employee
from app.core.security import hash_password


def create_employee(data: EmployeeCreate, db: Session) -> EmployeeRead:
    """
    Создаёт нового сотрудника с хешированным паролем.

    Args:
        data (EmployeeCreate): Данные для создания сотрудника: ФИО, role_id, телефон, логин, пароль.
        db (Session): Сессия базы данных SQLAlchemy.

    Returns:
        EmployeeRead: Созданный сотрудник (без пароля).

    Raises:
        HTTPException: Если пользователь с таким username уже существует (400).
    """
    existing = db.query(Employee).filter(Employee.username == data.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Имя пользователя уже существует")

    employee = Employee(
        last_name=data.last_name,
        first_name=data.first_name,
        patronymic=data.patronymic or "",
        role_id=data.role_id,
        phone=data.phone,
        username=data.username,
        password_hash=hash_password(data.password)
    )
    db.add(employee)
    db.commit()
    db.refresh(employee)
    return employee


def get_all_employees(db: Session) -> list[EmployeeRead]:
    """
    Возвращает список всех сотрудников.

    Args:
        db (Session): Сессия базы данных SQLAlchemy.

    Returns:
        list[EmployeeRead]: Список всех сотрудников.
    """
    return db.query(Employee).all()


def get_employee_by_id(employee_id: int, db: Session) -> EmployeeRead:
    """
    Получает сотрудника по его уникальному идентификатору.

    Args:
        employee_id (int): ID сотрудника.
        db (Session): Сессия базы данных SQLAlchemy.

    Returns:
        EmployeeRead: Найденный сотрудник.

    Raises:
        HTTPException: Если сотрудник не найден (404).
    """
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Сотрудник не найден")
    return employee


def update_employee(employee_id: int, data: EmployeeUpdate, db: Session) -> EmployeeRead:
    """
    Обновляет данные существующего сотрудника (кроме пароля и username).

    Args:
        employee_id (int): ID обновляемого сотрудника.
        data (EmployeeUpdate): Обновлённые данные: ФИО, role_id, телефон (опционально).
        db (Session): Сессия базы данных SQLAlchemy.

    Returns:
        EmployeeRead: Обновлённый сотрудник.

    Raises:
        HTTPException: Если сотрудник не найден (404).
    """
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Сотрудник не найден")

    if data.last_name is not None:
        employee.last_name = data.last_name
    if data.first_name is not None:
        employee.first_name = data.first_name
    if data.patronymic is not None:
        employee.patronymic = data.patronymic
    if data.role_id is not None:      
        employee.role_id = data.role_id
    if data.phone is not None:
        employee.phone = data.phone

    db.commit()
    db.refresh(employee)
    return employee


def delete_employee(employee_id: int, db: Session) -> dict[str, str]:
    """
    Удаляет сотрудника из системы по его ID.

    Args:
        employee_id (int): ID удаляемого сотрудника.
        db (Session): Сессия базы данных SQLAlchemy.

    Returns:
        dict[str, str]: Подтверждение удаления в формате {"status": "deleted"}.

    Raises:
        HTTPException: Если сотрудник не найден (404).
    """
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Сотрудник не найден")

    db.delete(employee)
    db.commit()
    return {"status": "deleted"}

def search_employees_by_name(query: str, db: Session) -> list[EmployeeRead]:
    """
    Выполняет поиск сотрудников по подстроке в поле full_name (регистронезависимо).

    Args:
        query (str): Строка для поиска в ФИО сотрудника.
        db (Session): Сессия базы данных SQLAlchemy.

    Returns:
        list[EmployeeRead]: Список сотрудников, у которых full_name содержит указанную подстроку.
    """
    q = f"%{query}%"
    employees = db.query(Employee).filter(
        or_(
            Employee.last_name.ilike(q),
            Employee.first_name.ilike(q),
            Employee.patronymic.ilike(q),
        )
    ).all()
    return employees