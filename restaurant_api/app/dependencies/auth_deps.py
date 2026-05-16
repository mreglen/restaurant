from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.security import decode_token
from app.core.database import get_db
from app.core.auth import AuthService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Извлекает текущего авторизованного пользователя по JWT-токену.

    Args:
        token (str): JWT-токен, переданный в заголовке Authorization.
        db (Session): Сессия базы данных.

    Returns:
        Employee: Объект текущего пользователя.

    Raises:
        HTTPException (401): Если токен недействителен, просрочен или пользователь не найден.
    """
    payload = decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный или просроченный токен"
        )
    user = AuthService.get_user_from_token(payload, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден"
        )
    return user


def require_roles(allowed_role_ids: list[int]):
    """
    Создаёт зависимость для проверки прав доступа по роли пользователя.

    Эта функция возвращает зависимость, которая проверяет,
    что идентификатор роли текущего пользователя содержится в списке разрешённых.

    Args:
        allowed_role_ids (list[int]): Список разрешённых идентификаторов ролей.

    Returns:
        function: Зависимость, возвращающая пользователя при успешной проверке.

    Raises:
        HTTPException (403): Если роль пользователя не входит в список разрешённых.
    """
    def checker(user=Depends(get_current_user)):
        if user.role_id not in allowed_role_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Доступ запрещён: недостаточно прав"
            )
        return user
    return checker