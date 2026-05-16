from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.routers import api_router
from app.routers.__init__v2__ import api_router_v2
from app.models import *  
from app.core.database import Base, engine  


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Контекстный менеджер lifespan для инициализации приложения.
    
    BUG-009 FIX: Заменяет устаревший @app.on_event('startup')
    """
    # Startup: создаём таблицы в БД при запуске
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown: можно добавить очистку ресурсов если нужно


app = FastAPI(title="Restaurant API", lifespan=lifespan)
"""Экземпляр FastAPI-приложения для управления ресторанной системой."""


app.include_router(api_router)
"""Подключает основной маршрутизатор API v1 из модуля `api_router`."""

app.include_router(api_router_v2)
"""Подключает основной маршрутизатор API v2 с исправленными багами."""


@app.get("/")
def root():
    """
    Корневой эндпоинт приложения.

    Возвращает приветственное сообщение, подтверждающее, что API запущено и работает.
    """
    return {"message": "Restaurant API"}