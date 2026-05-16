from pydantic import BaseModel


class OrderItemBase(BaseModel):
    """
    Базовая cхема позиции заказа.

    Определяет блюдо и количество — основные атрибуты любой позиции в заказе.
    """
    dish_id: int
    quantity: int


class OrderItemCreate(OrderItemBase):
    """
    Схема для создания позиции заказа.

    Используется при оформлении нового заказа. Наследует все поля от OrderItemBase.
    """
    pass


class OrderItemRead(OrderItemBase):
    """
    Схема для чтения данных позиции заказа.

    Включает идентификатор позиции и цену блюда на момент оформления заказа.
    Поддерживает загрузку из ORM-объекта.
    """
    id: int
    price: float

    class Config:
        orm_mode = True


class OrderBase(BaseModel):
    """
    Базовая cхема заказа.

    Содержит номер столика и опциональный идентификатор клиента.
    Используется как основа для создания, обновления и чтения заказов.
    """
    table_number: int
    client_id: int | None = None


class OrderCreate(OrderBase):
    """
    Схема для создания нового заказа.

    Расширяет OrderBase списком позиций (items), из которых состоит заказ.
    """
    items: list[OrderItemCreate]


class OrderUpdate(BaseModel):
    """
    Схема для частичного обновления заказа.

    Позволяет изменить номер столика и/или привязку к клиенту.
    Все поля опциональны.
    """
    table_number: int | None = None
    client_id: int | None = None


class OrderRead(OrderBase):
    """
    Схема для чтения полных данных заказа.

    Включает идентификатор заказа, итоговую стоимость и список позиций.
    Поддерживает загрузку из ORM-объекта благодаря orm_mode.
    """
    id: int
    total_price: float
    items: list[OrderItemRead]

    class Config:
        orm_mode = True