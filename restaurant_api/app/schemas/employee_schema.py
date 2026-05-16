from pydantic import BaseModel, Field
from typing import Optional


class EmployeeBase(BaseModel):
    """
    Базовая схема сотрудника.

    Содержит общие поля, относящиеся к личной информации и роли сотрудника.
    """
    last_name: str = Field(..., min_length=1, description="Фамилия")
    first_name: str = Field(..., min_length=1, description="Имя")
    patronymic: str = Field(default="", description="Отчество")
    role_id: int
    phone: Optional[str] = None


class EmployeeCreate(EmployeeBase):
    """
    Схема для создания нового сотрудника.

    Расширяет EmployeeBase учетными данными. Пароль передается в открытом виде
    и должен хэшироваться с использованием Argon2 перед сохранением в БД.
    """
    username: str
    password: str


class EmployeeUpdate(BaseModel):
    """
    Схема для частичного обновления данных сотрудника.

    Все поля опциональны, что позволяет изменять только указанные атрибуты.
    """
    last_name: Optional[str] = None
    first_name: Optional[str] = None
    patronymic: Optional[str] = None
    role_id: Optional[int] = None
    phone: Optional[str] = None


class EmployeeRead(EmployeeBase):
    """
    Схема для чтения данных сотрудника, включая идентификатор и имя пользователя.

    Не включает пароль или другие чувствительные данные. Поддерживает загрузку из ORM.
    """
    id: int
    username: str

    class Config:
        from_attributes = True
