from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.role import Role
from app.schemas.role_schema import RoleCreate


def create_role(data: RoleCreate, db: Session):
    """
    Создаёт новую роль в системе.

    Args:
        data (RoleCreate): Данные для создания роли, включая название и описание.
        db (Session): Сессия базы данных.

    Returns:
        Role: Созданная роль.
    """
    db_role = Role(name=data.name, description=data.description)
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role


def get_all_roles(db: Session):
    """
    Возвращает список всех ролей в системе.

    Args:
        db (Session): Сессия базы данных.

    Returns:
        List[Role]: Список всех ролей.
    """
    return db.query(Role).all()


def get_role_by_id(role_id: int, db: Session):
    """
    Возвращает роль по её идентификатору.

    Args:
        role_id (int): Идентификатор роли.
        db (Session): Сессия базы данных.

    Returns:
        Role | None: Найденная роль или None, если не найдена.
    """
    return db.query(Role).filter(Role.id == role_id).first()


def update_role(role_id: int, data: RoleCreate, db: Session):
    """
    Обновляет существующую роль.

    Args:
        role_id (int): Идентификатор обновляемой роли.
        data (RoleCreate): Новые данные для роли.
        db (Session): Сессия базы данных.

    Returns:
        Role: Обновлённая роль.

    Raises:
        HTTPException (404): Если роль с указанным ID не найдена.
    """
    role = get_role_by_id(role_id, db)
    if not role:
        raise HTTPException(status_code=404, detail="Роль не найдена")

    role.name = data.name
    role.description = data.description
    db.commit()
    db.refresh(role)
    return role


def delete_role(role_id: int, db: Session):
    """
    Удаляет роль по её идентификатору.

    Args:
        role_id (int): Идентификатор удаляемой роли.
        db (Session): Сессия базы данных.

    Returns:
        dict: Словарь с ключом 'deleted' и значением True, если роль удалена,
              или False, если роль не найдена.

    Raises:
        HTTPException (404): Если роль с указанным ID не найдена.
    """
    role = get_role_by_id(role_id, db)
    if not role:
        raise HTTPException(status_code=404, detail="Роль не найдена")

    db.delete(role)
    db.commit()
    return {"deleted": True}

def search_roles_by_name(query: str, db: Session):
    """
    Выполняет поиск ролей по подстроке в названии (регистронезависимо).

    Args:
        query (str): Строка для поиска в поле name.
        db (Session): Сессия базы данных SQLAlchemy.

    Returns:
        list[Role]: Список ролей, у которых название содержит указанную подстроку.
    """
    return db.query(Role).filter(Role.name.ilike(f"%{query}%")).all()