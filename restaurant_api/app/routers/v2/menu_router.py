from typing import List
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.schemas.v2.menu_schema import MenuCreate, MenuRead, MenuUpdate
from app.controllers.v2.menu_controller import (
    create_menu,
    get_all_menus,
    get_menu_by_id,
    search_menus_by_name,
    update_menu,
    delete_menu,
    export_menu_to_docx,
    export_menu_to_xlsx,
)
from app.core.database import get_db
from app.dependencies.auth_deps import get_current_user, require_roles

router = APIRouter(prefix="/menus", tags=["Menus"])

"""Роли которым предоставлен доступ"""
ADMIN_ROLE_ID = 1
MANAGER_ROLE_ID = 2
MANAGER_AND_ADMIN = [MANAGER_ROLE_ID, ADMIN_ROLE_ID]


@router.post(
    "/",
    response_model=MenuRead,
    dependencies=[Depends(require_roles(MANAGER_AND_ADMIN))]
)
def create_menu_endpoint(data: MenuCreate, db: Session = Depends(get_db)):
    """
    Создаёт новое меню. Доступно пользователям с ролью 'manager' (ID=2) или 'admin' (ID=1).
    """
    return create_menu(data, db)


@router.get(
    "/",
    response_model=list[MenuRead]
)
def get_all_menus_endpoint(db: Session = Depends(get_db)):
    """
    Возвращает список всех меню. Доступно всем (публичный эндпоинт).
    """
    return get_all_menus(db)


# BUG-003 FIX: Маршрут /search/ должен быть ДО /{menu_id}
@router.get("/search/", response_model=List[MenuRead], dependencies=[Depends(get_current_user)])
def search_menus(
    q: str = Query(..., min_length=1, description="Подстрока для поиска в названии меню"),
    db: Session = Depends(get_db),
    
):
    """
    Выполняет поиск меню по части названия (регистронезависимо).
    Доступно только пользователям с ролью ADMIN или MANAGER.

    - **q**: Часть названия меню (минимум 1 символ).
    """
    return search_menus_by_name(q, db)


@router.get(
    "/{menu_id}",
    response_model=MenuRead
)
def get_menu_endpoint(menu_id: int, db: Session = Depends(get_db)):
    """
    Возвращает данные меню по ID. Доступно всем (публичный эндпоинт).
    """
    return get_menu_by_id(menu_id, db)


@router.put(
    "/{menu_id}",
    response_model=MenuRead,
    dependencies=[Depends(require_roles(MANAGER_AND_ADMIN))]
)
def update_menu_endpoint(menu_id: int, data: MenuUpdate, db: Session = Depends(get_db)):
    """
    Обновляет меню (название и/или состав блюд). Доступно пользователям с ролью 'manager' или 'admin'.
    """
    return update_menu(menu_id, data, db)


@router.delete(
    "/{menu_id}",
    dependencies=[Depends(require_roles(MANAGER_AND_ADMIN))]
)
def delete_menu_endpoint(menu_id: int, db: Session = Depends(get_db)):
    """
    Удаляет меню и все его связи с блюдами. Доступно пользователям с ролью 'manager' или 'admin'.
    """
    return delete_menu(menu_id, db)


# BUG-004 FIX: Убран дублирующий get_current_user из dependencies
@router.get("/{menu_id}/export/docx")
def export_menu_docx_endpoint(menu_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    """
    Экспортирует меню в формат DOCX. Доступно только пользователям с ролями 'manager' или 'admin'.
    """
    if user.role_id not in MANAGER_AND_ADMIN:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Access denied")

    file_stream = export_menu_to_docx(menu_id, user.role_id, db)
    return StreamingResponse(
        file_stream,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f"attachment; filename=menu_{menu_id}.docx"}
    )


# BUG-004 FIX: Убран дублирующий get_current_user из dependencies
@router.get("/{menu_id}/export/xlsx")
def export_menu_xlsx_endpoint(menu_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    """
    Экспортирует меню в формат XLSX. Доступно только пользователям с ролями 'manager' или 'admin'.
    """
    if user.role_id not in MANAGER_AND_ADMIN:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Access denied")

    file_stream = export_menu_to_xlsx(menu_id, user.role_id, db)
    return StreamingResponse(
        file_stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=menu_{menu_id}.xlsx"}
    )