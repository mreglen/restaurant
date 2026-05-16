from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Order(Base):
    """
    Модель заказа.

    Представляет заказ, сделанный клиентом (или за столиком без привязки к клиенту).
    Содержит информацию о номере столика, общей стоимости и связанных позициях заказа.

    Атрибуты:
        id (int): Уникальный идентификатор заказа.
        client_id (int, optional): Идентификатор клиента (внешний ключ на таблицу clients). Может быть null, если заказ не привязан к клиенту.
        table_number (int): Номер столика, для которого оформлен заказ (обязательное поле).
        total_price (float): Общая стоимость заказа. По умолчанию — 0.
        client (Client): Связанный клиент (может быть None).
        items (List[OrderItem]): Список позиций в заказе.
    """

    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=True)
    table_number = Column(Integer, nullable=False)

    total_price = Column(Float, default=0)

    client = relationship("Client", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")