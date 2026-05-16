from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class OrderItem(Base):
    """
    Модель позиции заказа.

    Представляет отдельную строку в заказе: какое блюдо, в каком количестве и по какой цене.
    Связывает заказ (Order) с конкретным блюдом (Dish).

    Атрибуты:
        id (int): Уникальный идентификатор позиции заказа.
        order_id (int): Идентификатор заказа (внешний ключ на таблицу orders).
        dish_id (int): Идентификатор блюда (внешний ключ на таблицу dishes).
        quantity (int): Количество единиц блюда (обязательное поле).
        price (float): Цена одной единицы блюда на момент оформления заказа (обязательное поле).
        order (Order): Связанный заказ.
        dish (Dish): Связанное блюдо.
    """

    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    dish_id = Column(Integer, ForeignKey("dishes.id"), nullable=False)

    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)

    order = relationship("Order", back_populates="items")
    dish = relationship("Dish", back_populates="order_items")