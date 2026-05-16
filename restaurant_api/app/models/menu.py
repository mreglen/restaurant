from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.core.database import Base


class Menu(Base):
    """
    Модель меню.

    Представляет набор блюд, сгруппированных под общим названием (например, «Завтрак», «Обед», «Барная карта»).
    Связан с блюдами через промежуточную таблицу MenuItem.

    Атрибуты:
        id (int): Уникальный идентификатор меню.
        name (str): Название меню (обязательное поле).
        items (List[MenuItem]): Список пунктов меню, связанных с этим меню.
    """

    __tablename__ = "menus"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

    items = relationship("MenuItem", back_populates="menu")