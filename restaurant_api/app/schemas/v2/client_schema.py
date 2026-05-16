from pydantic import BaseModel, Field


class ClientBase(BaseModel):
    """
    Базовая схема клиента.

    Содержит общие поля, используемые при создании, обновлении и чтении данных клиента.
    """
    last_name: str = Field(..., min_length=1, description="Фамилия")
    first_name: str = Field(..., min_length=1, description="Имя")
    patronymic: str = Field(default="", description="Отчество")
    phone: str | None = None
    is_vip: bool = False
    bonus_points: int = 0


class ClientCreate(ClientBase):
    """
    Схема для создания нового клиента.

    Наследует все поля от ClientBase; дополнительных полей не требует.
    """
    pass


class ClientUpdate(BaseModel):
    """
    Схема для частичного обновления данных клиента.

    Все поля опциональны — позволяет обновлять только указанные атрибуты.
    """
    last_name: str | None = None
    first_name: str | None = None
    patronymic: str | None = None
    phone: str | None = None
    is_vip: bool | None = None
    bonus_points: int | None = None


class ClientRead(ClientBase):
    """
    Схема для чтения данных клиента, включая идентификатор.

    Используется при возврате данных из API. Поддерживает загрузку из ORM-объекта.
    """
    id: int

    class Config:
        orm_mode = True
