"""
Контроллер ингредиентов — CRUD + поиск.
"""
from core.controllers.base import APIClient


class IngredientController:
    """Контроллер для работы с эндпоинтами /ingredients."""

    def __init__(self, request=None):
        self._client = APIClient(request)

    def list(self) -> list:
        """GET /ingredients/ — список всех ингредиентов."""
        return self._client.get('/ingredients/') or []

    def search(self, q: str) -> list:
        """GET /ingredients/search/?q=... — поиск по названию."""
        return self._client.get('/ingredients/search/', params={'q': q}) or []

    def get(self, ingredient_id: int) -> dict:
        """GET /ingredients/{ingredient_id}/"""
        return self._client.get(f'/ingredients/{ingredient_id}/')

    def create(self, data: dict) -> dict:
        """POST /ingredients/"""
        return self._client.post('/ingredients/', data)

    def update(self, ingredient_id: int, data: dict) -> dict:
        """PUT /ingredients/{ingredient_id}/"""
        return self._client.put(f'/ingredients/{ingredient_id}/', data)

    def delete(self, ingredient_id: int) -> None:
        """DELETE /ingredients/{ingredient_id}/"""
        self._client.delete(f'/ingredients/{ingredient_id}/')
