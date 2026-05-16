from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class TableAssignment(Base):
    """
    Модель закрепления столика за сотрудником.

    Определяет, какой сотрудник (обычно официант) обслуживает конкретный столик.
    Один сотрудник может быть закреплён за несколькими столиками.

    Атрибуты:
        id (int): Уникальный идентификатор записи о закреплении.
        table_number (int): Номер столика (обязательное поле).
        employee_id (int): Идентификатор сотрудника (внешний ключ на таблицу employees).
        employee (Employee): Сотрудник, закреплённый за столиком.
    """

    __tablename__ = "table_assignments"

    id = Column(Integer, primary_key=True, index=True)
    table_number = Column(Integer, nullable=False)

    employee_id = Column(Integer, ForeignKey("employees.id"))

    employee = relationship("Employee", back_populates="tables")