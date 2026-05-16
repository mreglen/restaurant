from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.core.config import settings


class Base(DeclarativeBase):
    """
    Базовый класс для всех моделей SQLAlchemy.

    Используется для автоматической регистрации моделей и создания таблиц
    с помощью `Base.metadata.create_all()`.
    """
    pass


engine = create_engine(
    settings.DATABASE_URL
)
"""Движок SQLAlchemy, подключённый к URL базы данных из настроек."""


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)
"""
Фабрика сессий SQLAlchemy.

Настроена с отключёнными autocommit и autoflush для явного управления транзакциями.
"""


def get_db():
    """
    Зависимость для получения сессии базы данных в FastAPI-эндпоинтах.

    Открывает новую сессию перед выполнением запроса и закрывает её после завершения,
    даже в случае возникновения исключения.
    
    Используется с yield для совместимости с FastAPI Depends().
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()