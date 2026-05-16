from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base


class Client(Base):
    """
    Модель клиента в системе.

    Представляет зарегистрированного клиента, который может оформлять заказы.
    Содержит личные данные клиента, информацию о статусе (VIP/обычный),
    а также накопленные бонусные баллы.

    Атрибуты:
        id (int): Уникальный идентификатор клиента.
        last_name (str): Фамилия.
        first_name (str): Имя.
        patronymic (str): Отчество (может быть пустым).
        phone (str, optional): Номер телефона клиента.
        is_vip (bool): Флаг VIP-статуса клиента. По умолчанию — False.
        bonus_points (int): Количество бонусных баллов. По умолчанию — 0.
        orders (List[Order]): Связанные с клиентом заказы (обратная связь с моделью Order).
    """

    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    last_name = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    patronymic = Column(String, nullable=False, default="")
    phone = Column(String, nullable=True)

    is_vip = Column(Boolean, default=False)
    bonus_points = Column(Integer, default=0)

    orders = relationship("Order", back_populates="client")