from fastapi import APIRouter
from app.routers.v2.auth_router import router as auth_router
from app.routers.v2.client_router import router as client_router
from app.routers.v2.dish_router import router as dish_router
from app.routers.v2.employee_router import router as employee_router
from app.routers.v2.ingredient_router import router as ingredient_router
from app.routers.v2.menu_router import router as menu_router
from app.routers.v2.order_router import router as order_router
from app.routers.v2.table_assignment_router import router as table_router
from app.routers.v2.role_router import router as role_router


api_router_v2 = APIRouter(prefix="/api/v2")
"""
Основной маршрутизатор API v2.

Объединяет все подмодули приложения версии v2
под общим префиксом `/api/v2`. Включает все исправления багов из отчета.
"""
api_router_v2.include_router(role_router)
api_router_v2.include_router(auth_router)
api_router_v2.include_router(client_router)
api_router_v2.include_router(dish_router)
api_router_v2.include_router(employee_router)
api_router_v2.include_router(ingredient_router)
api_router_v2.include_router(menu_router)
api_router_v2.include_router(order_router)
api_router_v2.include_router(table_router)
