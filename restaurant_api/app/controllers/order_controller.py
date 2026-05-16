from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import List

from app.schemas.order_schema import OrderCreate, OrderUpdate, OrderRead, OrderItemRead
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.dish import Dish
from app.models.client import Client


def create_order(data: OrderCreate, db: Session) -> OrderRead:
    """
    Создаёт новый заказ, включая его позиции.

    Args:
        data (OrderCreate): Данные заказа: номер стола, ID клиента (опционально), список блюд с количеством.
        db (Session): Сессия базы данных SQLAlchemy.

    Returns:
        OrderRead: Созданный заказ с полным списком позиций и итоговой стоимостью.

    Raises:
        HTTPException: Если указан несуществующий клиент (404) или блюдо (404).
    """
    if data.client_id is not None:
        client = db.query(Client).filter(Client.id == data.client_id).first()
        if not client:
            raise HTTPException(status_code=404, detail="Клиент не найден")

    order = Order(table_number=data.table_number, client_id=data.client_id, total_price=0)
    db.add(order)
    db.commit()
    db.refresh(order)

    total = 0
    created_items = []

    for item in data.items:
        dish = db.query(Dish).filter(Dish.id == item.dish_id).first()
        if not dish:
            raise HTTPException(status_code=404, detail=f"Идентификатор блюда {item.dish_id} не найден")

        price = dish.price * item.quantity
        total += price

        order_item = OrderItem(
            order_id=order.id,
            dish_id=item.dish_id,
            quantity=item.quantity,
            price=price
        )
        db.add(order_item)
        created_items.append(order_item)

    order.total_price = total
    db.commit()
    db.refresh(order)

    return OrderRead(
        id=order.id,
        table_number=order.table_number,
        client_id=order.client_id,
        total_price=order.total_price,
        items=[
            OrderItemRead(
                id=i.id,
                dish_id=i.dish_id,
                quantity=i.quantity,
                price=i.price
            )
            for i in created_items
        ]
    )


def get_all_orders(db: Session) -> List[OrderRead]:
    """
    Возвращает список всех заказов со всеми позициями.

    Args:
        db (Session): Сессия базы данных SQLAlchemy.

    Returns:
        list[OrderRead]: Список всех заказов.
    """
    orders = db.query(Order).all()
    result = []
    for order in orders:
        result.append(OrderRead(
            id=order.id,
            table_number=order.table_number,
            client_id=order.client_id,
            total_price=order.total_price,
            items=[
                OrderItemRead(
                    id=item.id,
                    dish_id=item.dish_id,
                    quantity=item.quantity,
                    price=item.price
                )
                for item in order.items if item.dish_id is not None
            ]
        ))
    return result


def get_order_by_id(order_id: int, db: Session) -> OrderRead:
    """
    Получает заказ по его уникальному идентификатору.

    Args:
        order_id (int): ID заказа.
        db (Session): Сессия базы данных SQLAlchemy.

    Returns:
        OrderRead: Найденный заказ с позициями.

    Raises:
        HTTPException: Если заказ не найден (404).
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")

    return OrderRead(
        id=order.id,
        table_number=order.table_number,
        client_id=order.client_id,
        total_price=order.total_price,
        items=[
            OrderItemRead(
                id=item.id,
                dish_id=item.dish_id,
                quantity=item.quantity,
                price=item.price
            )
            for item in order.items
        ]
    )


def update_order(order_id: int, data:  OrderUpdate, db: Session) -> OrderRead:
    """
    Обновляет основные данные заказа (номер стола, клиент). Позиции заказа не изменяются.

    Args:
        order_id (int): ID обновляемого заказа.
        data (OrderUpdate): Обновлённые данные заказа (опциональные поля).
        db (Session): Сессия базы данных SQLAlchemy.

    Returns:
        OrderRead: Обновлённый заказ.

    Raises:
        HTTPException: Если заказ не найден (404) или указан несуществующий клиент (404).
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")

    if data.table_number is not None:
        order.table_number = data.table_number

    if data.client_id is not None:
        client = db.query(Client).filter(Client.id == data.client_id).first()
        if not client:
            raise HTTPException(status_code=404, detail="Клиент не найден")
        order.client_id = data.client_id

    db.commit()
    db.refresh(order)

    return OrderRead(
        id=order.id,
        table_number=order.table_number,
        client_id=order.client_id,
        total_price=order.total_price,
        items=[
            OrderItemRead(
                id=item.id,
                dish_id=item.dish_id,
                quantity=item.quantity,
                price=item.price
            )
            for item in order.items
        ]
    )


def delete_order(order_id: int, db: Session) -> dict[str, str]:
    """
    Удаляет заказ и все его позиции.

    Args:
        order_id (int): ID удаляемого заказа.
        db (Session): Сессия базы данных SQLAlchemy.

    Returns:
        dict[str, str]: Подтверждение удаления: {"status": "deleted"}.

    Raises:
        HTTPException: Если заказ не найден (404).
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")

    db.query(OrderItem).filter(OrderItem.order_id == order_id).delete()
    db.delete(order)
    db.commit()
    return {"status": "deleted"}

