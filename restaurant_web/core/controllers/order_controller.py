"""
Контроллер заказов — CRUD.
"""
from core.controllers.base import APIClient


class OrderController:
    """Контроллер для работы с эндпоинтами /orders."""

    def __init__(self, request=None):
        self._client = APIClient(request)

    def list(self) -> list:
        """GET /orders/ — список всех заказов."""
        return self._client.get('/orders/') or []

    def get(self, order_id: int) -> dict:
        """GET /orders/{order_id}/"""
        return self._client.get(f'/orders/{order_id}/')

    def create(self, data: dict) -> dict:
        """POST /orders/"""
        return self._client.post('/orders/', data)

    def update(self, order_id: int, data: dict) -> dict:
        """PUT /orders/{order_id}/"""
        return self._client.put(f'/orders/{order_id}/', data)

    def delete(self, order_id: int) -> None:
        """DELETE /orders/{order_id}/"""
        self._client.delete(f'/orders/{order_id}/')
