from pydantic import BaseModel, Field


class DishBase(BaseModel):
    """
    Базовая схема блюда.

    Содержит основные атрибуты блюда: название, описание и цену.
    Используется как родительский класс для операций создания, обновления и чтения.
    """
    name: str
    description: str | None = None
    price: float = Field(gt=0, description="Цена должна быть > 0")


class DishCreate(DishBase):
    """
    Схема для создания нового блюда.

    Расширяет DishBase списком идентификаторов ингредиентов (ingredient_ids),
    которые будут связаны с блюдом через промежуточную таблицу.
    """
    ingredient_ids: list[int] = []  


class DishUpdate(BaseModel):
    """
    Схема для частичного обновления блюда.

    Все поля опциональны, включая список идентификаторов ингредиентов,
    что позволяет обновлять как основные данные, так и состав блюда.
    """
    name: str | None = None
    description: str | None = None
    price: float | None = None
    ingredient_ids: list[int] | None = None


class DishRead(DishBase):
    """
    Схема для чтения данных о блюде, включая его идентификатор и состав.

    Возвращает ID блюда и список ID ингредиентов (упрощённое представление связей).
    Поддерживает загрузку из ORM-объекта благодаря включённому orm_mode.
    """
    id: int
    ingredients: list[int] = [] 

    class Config:
        from_attributes = True