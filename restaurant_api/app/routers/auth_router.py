from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.schemas.auth_schema import AuthRegister, AuthLogin, Token
from app.controllers.auth_controller import register_user, login_user
from app.core.database import get_db

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=Token)
def register(data: AuthRegister, db: Session = Depends(get_db)):
    """
    Эндпоинт регистрации нового пользователя.
    """
    try:
        token = register_user(data, db)
        return {"access_token": token}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=Token)
def login(
    data: AuthLogin = Depends(AuthLogin.as_form),
    db: Session = Depends(get_db)
):
    """
    Эндпоинт входа существующего пользователя.
    """
    try:
        token = login_user(data, db)
        return {"access_token": token}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))