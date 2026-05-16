from sqlalchemy import or_
from sqlalchemy.orm import Session
from app.schemas.client_schema import ClientCreate, ClientUpdate
from app.models.client import Client
from fastapi import HTTPException


def create_client(data: ClientCreate, db: Session) -> Client:
    """
    Создаёт нового клиента в системе.

    Args:
        data (ClientCreate): Данные для создания клиента: ФИО, телефон, флаг VIP, бонусные баллы.
        db (Session): Сессия базы данных SQLAlchemy.

    Returns:
        Client: Созданный объект клиента с присвоенным ID.
    """
    client = Client(
        last_name=data.last_name,
        first_name=data.first_name,
        patronymic=data.patronymic or "",
        phone=data.phone,
        is_vip=data.is_vip,
        bonus_points=data.bonus_points,
    )
    db.add(client)
    db.commit()
    db.refresh(client)
    return client


def get_all_clients(db: Session) -> list[Client]:
    """
    Возвращает список всех клиентов.

    Args:
        db (Session): Сессия базы данных SQLAlchemy.

    Returns:
        list[Client]: Список всех клиентов в системе.
    """
    return db.query(Client).all()


def get_client_by_id(client_id: int, db: Session) -> Client:
    """
    Получает клиента по его уникальному идентификатору.

    Args:
        client_id (int): ID клиента.
        db (Session): Сессия базы данных SQLAlchemy.

    Returns:
        Client: Найденный клиент.

    Raises:
        HTTPException: Если клиент с указанным ID не найден (404).
    """
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Клиент не найден")
    return client


def search_clients_by_name(query: str, db: Session) -> list[Client]:
    """
    Выполняет поиск клиентов по части ФИО (регистронезависимо).

    Args:
        query (str): Строка для поиска в поле full_name.
        db (Session): Сессия базы данных SQLAlchemy.

    Returns:
        list[Client]: Список клиентов, у которых full_name содержит query.
    """
    q = f"%{query}%"
    return db.query(Client).filter(
        or_(
            Client.last_name.ilike(q),
            Client.first_name.ilike(q),
            Client.patronymic.ilike(q),
        )
    ).all()


def update_client(client_id: int, data: ClientUpdate, db: Session) -> Client:
    """
    Обновляет информацию о клиенте.

    Args:
        client_id (int): ID обновляемого клиента.
        data (ClientUpdate): Обновлённые поля клиента (опциональные).
        db (Session): Сессия базы данных SQLAlchemy.

    Returns:
        Client: Обновлённый объект клиента.

    Raises:
        HTTPException: Если клиент с указанным ID не найден (404).
    """
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Клиент не найден")

    if data.last_name is not None:
        client.last_name = data.last_name
    if data.first_name is not None:
        client.first_name = data.first_name
    if data.patronymic is not None:
        client.patronymic = data.patronymic
    if data.phone is not None:
        client.phone = data.phone
    if data.is_vip is not None:
        client.is_vip = data.is_vip
    if data.bonus_points is not None:
        client.bonus_points = data.bonus_points

    db.commit()
    db.refresh(client)
    return client


def delete_client(client_id: int, db: Session) -> dict[str, str]:
    """
    Удаляет клиента из системы по его ID.

    Args:
        client_id (int): ID удаляемого клиента.
        db (Session): Сессия базы данных SQLAlchemy.

    Returns:
        dict[str, str]: Словарь с подтверждением удаления: {"status": "deleted"}.

    Raises:
        HTTPException: Если клиент с указанным ID не найден (404).
    """
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Клиент не найден")

    db.delete(client)
    db.commit()
    return {"status": "deleted"}