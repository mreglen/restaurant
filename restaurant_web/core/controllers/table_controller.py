"""
Контроллер назначений столиков — CRUD.
"""
from core.controllers.base import APIClient


class TableController:
    """Контроллер для работы с эндпоинтами /tables."""

    def __init__(self, request=None):
        self._client = APIClient(request)

    def list(self) -> list:
        """GET /tables/ — список всех назначений столиков."""
        return self._client.get('/tables/') or []

    def get(self, assignment_id: int) -> dict:
        """GET /tables/{assignment_id}/"""
        return self._client.get(f'/tables/{assignment_id}/')

    def create(self, data: dict) -> dict:
        """POST /tables/"""
        return self._client.post('/tables/', data)

    def update(self, assignment_id: int, data: dict) -> dict:
        """PUT /tables/{assignment_id}/"""
        return self._client.put(f'/tables/{assignment_id}/', data)

    def delete(self, assignment_id: int) -> None:
        """DELETE /tables/{assignment_id}/"""
        self._client.delete(f'/tables/{assignment_id}/')
