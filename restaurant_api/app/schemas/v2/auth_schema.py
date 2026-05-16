from fastapi import Form
from pydantic import BaseModel, Field


class AuthRegister(BaseModel):
    """
    Схема данных для регистрации нового сотрудника.

    Используется при создании учётной записи сотрудника через API.
    """
    last_name: str = Field(..., min_length=1, description="Фамилия")
    first_name: str = Field(..., min_length=1, description="Имя")
    patronymic: str = Field(default="", description="Отчество")
    role: int
    phone: str | None = None
    username: str
    password: str


class AuthLogin(BaseModel):
    """
    Схема данных для входа в систему.

    Поддерживает создание экземпляра из формы (например, для OAuth2-совместимых эндпоинтов).
    """
    username: str
    password: str

    @classmethod
    def as_form(
        cls,
        username: str = Form(...),
        password: str = Form(...)
    ) -> "AuthLogin":
        """
        Создаёт экземпляр модели из данных формы.

        Используется в FastAPI для обработки запросов с Content-Type: application/x-www-form-urlencoded,
        например, при аутентификации через OAuth2 password flow.
        """
        return cls(username=username, password=password)


class Token(BaseModel):
    """
    Схема JWT-токена доступа.

    Возвращается клиенту после успешной аутентификации.
    """
    access_token: str
    token_type: str = "bearer"
