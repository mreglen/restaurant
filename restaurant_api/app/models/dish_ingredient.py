from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class DishIngredient(Base):
    """
    Промежуточная модель для связи блюда и ингредиента (многие-ко-многим).

    Определяет, какие ингредиенты входят в состав конкретного блюда.
    Используется для реализации связи многие-ко-многим между моделями Dish и Ingredient.

    Атрибуты:
        id (int): Уникальный идентификатор записи.
        dish_id (int): Идентификатор блюда (внешний ключ на таблицу dishes).
        ingredient_id (int): Идентификатор ингредиента (внешний ключ на таблицу ingredients).
        dish (Dish): Связанное блюдо.
        ingredient (Ingredient): Связанный ингредиент.
    """

    __tablename__ = "dish_ingredient"

    id = Column(Integer, primary_key=True, index=True)
    dish_id = Column(Integer, ForeignKey("dishes.id"))
    ingredient_id = Column(Integer, ForeignKey("ingredients.id"))

    dish = relationship("Dish", back_populates="ingredients")
    ingredient = relationship("Ingredient", back_populates="dishes")