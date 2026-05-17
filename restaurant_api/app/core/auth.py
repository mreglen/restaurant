from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.employee import Employee
from app.core.security import hash_password, verify_password, create_access_token
from app.schemas.auth_schema import AuthLogin, AuthRegister


class AuthService:
    @staticmethod
    def register(data: AuthRegister, db: Session) -> str:
        """
        Регистрирует нового пользователя (сотрудника) в системе.

        Args:
            data (AuthRegister): Данные для регистрации: ФИО, логин, пароль, телефон и ID роли.
            db (Session): Сессия базы данных.

        Returns:
            str: JWT-токен для нового пользователя.

        Raises:
            HTTPException (400): Если имя пользователя уже занято.
        """
        existing = db.query(Employee).filter(Employee.username == data.username).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Имя пользователя уже занято"
            )

        # Публичная регистрация — только роль официанта (id=3).
        waiter_role_id = 3
        user = Employee(
            last_name=data.last_name,
            first_name=data.first_name,
            patronymic=data.patronymic or "",
            username=data.username,
            password_hash=hash_password(data.password),
            role_id=waiter_role_id,
            phone=data.phone
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        token = create_access_token({
            "sub": user.username,
            "role_id": user.role_id
        })
        return token

    @staticmethod
    def login(data: AuthLogin, db: Session) -> str:
        """
        Выполняет аутентификацию пользователя по логину и паролю.

        Args:
            data (AuthLogin): Логин и пароль пользователя.
            db (Session): Сессия базы данных.

        Returns:
            str: JWT-токен при успешной аутентификации.

        Raises:
            HTTPException (401): Если логин или пароль неверны.
        """
        user = db.query(Employee).filter(Employee.username == data.username).first()
        if not user or not verify_password(data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверное имя пользователя или пароль"
            )

        token = create_access_token({
            "sub": user.username,
            "role_id": user.role_id
        })
        return token

    @staticmethod
    def get_user_from_token(token_payload: dict, db: Session):
        """
        Извлекает пользователя из базы данных по данным из JWT-токена.

        Args:
            token_payload (dict): Декодированные данные токена (payload).
            db (Session): Сессия базы данных.

        Returns:
            Employee | None: Найденный пользователь или None, если логин отсутствует
            или пользователь не найден.
        """
        username = token_payload.get("sub")
        if not username:
            return None
        return db.query(Employee).filter(Employee.username == username).first()