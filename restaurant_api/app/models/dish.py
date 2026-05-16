from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship
from app.core.database import Base


class Dish(Base):
    """
    Модель блюда в меню.

    Представляет конкретное блюдо, доступное для заказа. Содержит название,
    описание, цену, а также связи с ингредиентами, пунктами меню и позициями заказов.

    Атрибуты:
        id (int): Уникальный идентификатор блюда.
        name (str): Название блюда (обязательное поле).
        description (str, optional): Описание блюда.
        price (float): Цена блюда (обязательное поле).
        ingredients (List[DishIngredient]): Список связанных записей в промежуточной таблице ингредиентов.
        menu_items (List[MenuItem]): Пункты меню, в которых используется это блюдо.
        order_items (List[OrderItem]): Позиции заказов, содержащие это блюдо.
    """

    __tablename__ = "dishes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Float, nullable=False)

    ingredients = relationship("DishIngredient", back_populates="dish")
    menu_items = relationship("MenuItem", back_populates="dish")
    order_items = relationship("OrderItem", back_populates="dish")