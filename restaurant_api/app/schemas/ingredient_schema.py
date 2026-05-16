from pydantic import BaseModel


class IngredientBase(BaseModel):
    """
    Базовая cхема ингредиента.

    Содержит основное поле — название ингредиента.
    Используется как родительский класс для операций создания, обновления и чтения.
    """
    name: str


class IngredientCreate(IngredientBase):
    """
    Схема для создания нового ингредиента.

    Наследует все поля от IngredientBase; дополнительных полей не требует.
    """
    pass


class IngredientUpdate(BaseModel):
    """
    Схема для частичного обновления ингредиента.

    Позволяет обновлять название ингредиента; поле опционально.
    """
    name: str | None = None


class IngredientRead(IngredientBase):
    """
    Схема для чтения данных ингредиента, включая его идентификатор.

    Поддерживает загрузку из ORM-объекта благодаря включённому orm_mode.
    """
    id: int

    class Config:
        orm_mode = True