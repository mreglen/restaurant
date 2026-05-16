from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Employee(Base):
    """
    Модель сотрудника.

    Представляет зарегистрированного пользователя с ролью, учётными данными
    и личной информацией. Используется для аутентификации и контроля доступа.

    Атрибуты:
        id (int): Уникальный идентификатор сотрудника.
        last_name (str): Фамилия.
        first_name (str): Имя.
        patronymic (str): Отчество (может быть пустым).
        phone (str | None): Номер телефона (необязательный).
        username (str): Уникальное имя пользователя для входа в систему.
        password_hash (str): Хеш пароля (хранится в зашифрованном виде).
        role_id (int): Внешний ключ, ссылающийся на роль из таблицы roles.
        role (Role): Связанная роль пользователя (relationship).
        tables (List[TableAssignment]): Список назначений на столы (relationship).
    """
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    last_name = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    patronymic = Column(String, nullable=False, default="")
    phone = Column(String, nullable=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)

    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    role = relationship("Role")

    tables = relationship("TableAssignment", back_populates="employee")