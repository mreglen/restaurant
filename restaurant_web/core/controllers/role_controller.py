"""
Контроллер ролей — CRUD + поиск.
"""
from core.controllers.base import APIClient


class RoleController:
    """Контроллер для работы с эндпоинтами /roles."""

    def __init__(self, request=None):
        self._client = APIClient(request)

    def list(self) -> list:
        """GET /roles/ — список всех ролей."""
        return self._client.get('/roles/') or []

    def search(self, q: str) -> list:
        """GET /roles/search/?q=... — поиск по названию."""
        return self._client.get('/roles/search/', params={'q': q}) or []

    def get(self, role_id: int) -> dict:
        """GET /roles/{role_id}/"""
        return self._client.get(f'/roles/{role_id}/')

    def create(self, data: dict) -> dict:
        """POST /roles/"""
        return self._client.post('/roles/', data)

    def update(self, role_id: int, data: dict) -> dict:
        """PUT /roles/{role_id}/"""
        return self._client.put(f'/roles/{role_id}/', data)

    def delete(self, role_id: int) -> None:
        """DELETE /roles/{role_id}/"""
        self._client.delete(f'/roles/{role_id}/')
