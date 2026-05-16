from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.core.database import Base


class Ingredient(Base):
    """
    Модель ингредиента.

    Представляет отдельный ингредиент, который может использоваться в составе блюд.
    Связан с блюдами через промежуточную таблицу DishIngredient.

    Атрибуты:
        id (int): Уникальный идентификатор ингредиента.
        name (str): Название ингредиента (обязательное поле).
        dishes (List[DishIngredient]): Список связей с блюдами, в которых используется этот ингредиент.
    """

    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

    dishes = relationship("DishIngredient", back_populates="ingredient")