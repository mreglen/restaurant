from pydantic import BaseModel


class TableAssignmentBase(BaseModel):
    """
    Базовая cхема закрепления столика за сотрудником.

    Содержит номер столика и идентификатор сотрудника, за которым он закреплён.
    """
    table_number: int
    employee_id: int


class TableAssignmentCreate(TableAssignmentBase):
    """
    Схема для создания новой записи о закреплении столика.

    Наследует все поля от TableAssignmentBase; дополнительных полей не требует.
    """
    pass


class TableAssignmentRead(TableAssignmentBase):
    """
    Схема для чтения данных о закреплении столика.

    Включает уникальный идентификатор записи в дополнение к базовым полям.
    Поддерживает загрузку из ORM-объекта благодаря включённому orm_mode.
    """
    id: int

    class Config:
        orm_mode = True