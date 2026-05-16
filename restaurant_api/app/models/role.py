from sqlalchemy import Column, Integer, String
from app.core.database import Base


class Role(Base):
    """
    Модель роли пользователя.

    Определяет доступные привилегии и функциональность для группы пользователей.
    Каждая роль имеет уникальное название и необязательное описание.

    Атрибуты:
        id (int): Уникальный идентификатор роли.
        name (str): Уникальное название роли (обязательное).
        description (str | None): Описание назначения или функций роли (необязательное).
    """
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)