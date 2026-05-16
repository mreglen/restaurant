from fastapi import APIRouter
from app.routers.auth_router import router as auth_router
from app.routers.client_router import router as client_router
from app.routers.dish_router import router as dish_router
from app.routers.employee_router import router as employee_router
from app.routers.ingredient_router import router as ingredient_router
from app.routers.menu_router import router as menu_router
from app.routers.order_router import router as order_router
from app.routers.table_assignment_router import router as table_router
from app.routers.role_router import router as role_router


api_router = APIRouter(prefix="/api/v1")
"""
Основной маршрутизатор API.

Объединяет все подмодули приложения
под общим префиксом `/api/v1`. Упрощает централизованное управление и подключение эндпоинтов.
"""
api_router.include_router(role_router)
api_router.include_router(auth_router)
api_router.include_router(client_router)
api_router.include_router(dish_router)
api_router.include_router(employee_router)
api_router.include_router(ingredient_router)
api_router.include_router(menu_router)
api_router.include_router(order_router)
api_router.include_router(table_router)