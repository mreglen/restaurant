from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.schemas.v2.role_schema import RoleCreate, RoleRead
from app.controllers.v2.role_controller import *
from app.core.database import get_db
from app.dependencies.auth_deps import require_roles

router = APIRouter(prefix="/roles", tags=["Roles"])

"""Роли которым предоставлен доступ"""
ADMIN_ROLE_ID = 1

@router.post("/", response_model=RoleRead, dependencies=[Depends(require_roles([ADMIN_ROLE_ID]))])
def create_role_endpoint(data: RoleCreate, db: Session = Depends(get_db)):
    return create_role(data, db)

@router.get("/", response_model=list[RoleRead], dependencies=[Depends(require_roles([ADMIN_ROLE_ID]))])
def list_roles(db: Session = Depends(get_db)):
    return get_all_roles(db)

@router.get("/{role_id}", response_model=RoleRead, dependencies=[Depends(require_roles([ADMIN_ROLE_ID]))])
def get_role(role_id: int, db: Session = Depends(get_db)):
    role = get_role_by_id(role_id, db)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role

@router.put("/{role_id}", response_model=RoleRead, dependencies=[Depends(require_roles([ADMIN_ROLE_ID]))])
def update_role_endpoint(role_id: int, data: RoleCreate, db: Session = Depends(get_db)):
    role = update_role(role_id, data, db)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role

@router.delete("/{role_id}", dependencies=[Depends(require_roles([ADMIN_ROLE_ID]))])
def delete_role_endpoint(role_id: int, db: Session = Depends(get_db)):
    result = delete_role(role_id, db)
    if not result["deleted"]:
        raise HTTPException(status_code=404, detail="Role not found")
    return {"message": "Role deleted"}

@router.get("/search/", response_model=List[RoleRead], dependencies=[Depends(require_roles([ADMIN_ROLE_ID]))])
def search_roles(
    q: str = Query(..., min_length=1, description="Подстрока для поиска в названии роли"),
    db: Session = Depends(get_db)
):
    """
    Выполняет поиск ролей по части названия (регистронезависимо).
    Доступно только пользователям с ролью ADMIN.

    - **q**: Часть названия роли (минимум 1 символ).
    """
    return search_roles_by_name(q, db)