"""
Контроллер блюд — CRUD + поиск.
"""
from core.controllers.base import APIClient


class DishController:
    """Контроллер для работы с эндпоинтами /dishes."""

    def __init__(self, request=None):
        self._client = APIClient(request)

    def list(self) -> list:
        """GET /dishes/ — список всех блюд."""
        return self._client.get('/dishes/') or []

    def search(self, q: str) -> list:
        """GET /dishes/search/?q=... — поиск по названию."""
        return self._client.get('/dishes/search/', params={'q': q}) or []

    def get(self, dish_id: int) -> dict:
        """GET /dishes/{dish_id}/"""
        return self._client.get(f'/dishes/{dish_id}/')

    def create(self, data: dict) -> dict:
        """POST /dishes/"""
        return self._client.post('/dishes/', data)

    def update(self, dish_id: int, data: dict) -> dict:
        """PUT /dishes/{dish_id}/"""
        return self._client.put(f'/dishes/{dish_id}/', data)

    def delete(self, dish_id: int) -> None:
        """DELETE /dishes/{dish_id}/"""
        self._client.delete(f'/dishes/{dish_id}/')
