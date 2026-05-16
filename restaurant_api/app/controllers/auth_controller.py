from sqlalchemy.orm import Session
from app.schemas.auth_schema import AuthRegister, AuthLogin
from app.core.auth import AuthService


def register_user(data: AuthRegister, db: Session) -> str:
    """
    Регистрирует нового пользователя с переданными данными.

    Args:
        data (AuthRegister): Данные для регистрации: email, телефон, пароль и т.д.
        db (Session): Сессия базы данных SQLAlchemy.

    Returns:
        str: JWT-токен доступа для зарегистрированного пользователя.

    Raises:
        ValueError: Если регистрация невозможна из-за некорректных данных или нарушения бизнес-логики.
    """
    return AuthService.register(data, db)


def login_user(data: AuthLogin, db: Session) -> str:
    """
    Выполняет аутентификацию пользователя и возвращает JWT-токен при успешном входе.

    Args:
        data (AuthLogin): Учётные данные для входа (например, email/телефон и пароль).
        db (Session): Сессия базы данных SQLAlchemy.

    Returns:
        str: JWT-токен доступа для аутентифицированного пользователя.

    Raises:
        ValueError: Если аутентификация не удалась (неверные учётные данные или пользователь не найден).
    """
    return AuthService.login(data, db)