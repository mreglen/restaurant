from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class MenuItem(Base):
    """
    Промежуточная модель для связи меню и блюд (многие-ко-многим).

    Определяет, какие блюда включены в конкретное меню.
    Используется для реализации связи многие-ко-многим между моделями Menu и Dish.

    Атрибуты:
        id (int): Уникальный идентификатор записи в меню.
        menu_id (int): Идентификатор меню (внешний ключ на таблицу menus).
        dish_id (int): Идентификатор блюда (внешний ключ на таблицу dishes).
        menu (Menu): Связанное меню.
        dish (Dish): Связанное блюдо.
    """

    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True, index=True)
    menu_id = Column(Integer, ForeignKey("menus.id"), nullable=False)
    dish_id = Column(Integer, ForeignKey("dishes.id"), nullable=False)

    menu = relationship("Menu", back_populates="items")
    dish = relationship("Dish", back_populates="menu_items")