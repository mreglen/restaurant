from pydantic import BaseModel


class MenuBase(BaseModel):
    """
    Базовая cхема меню.

    Содержит основное поле — название меню.
    Используется как родительский класс для операций создания, обновления и чтения.
    """
    name: str


class MenuCreate(MenuBase):
    """
    Схема для создания нового меню.

    Расширяет MenuBase списком идентификаторов блюд (dish_ids),
    которые будут включены в меню через промежуточную таблицу MenuItem.
    """
    dish_ids: list[int] = []


class MenuUpdate(BaseModel):
    """
    Схема для частичного обновления меню.

    Позволяет изменить название меню и/или состав блюд.
    Все поля опциональны.
    """
    name: str | None = None
    dish_ids: list[int] | None = None


class MenuRead(MenuBase):
    """
    Схема для чтения данных меню, включая его идентификатор и состав.

    Поле `dish_ids` содержит список ID блюд, входящих в меню (упрощённое представление связей).
    Поддерживает загрузку из ORM-объекта благодаря включённому orm_mode.
    """
    id: int
    dish_ids: list[int] = []  # Список ID блюд, включённых в меню

    class Config:
        from_attributes = True