"""
Контроллер клиентов — CRUD + поиск + массовое удаление.
"""
from core.controllers.base import APIClient


class ClientController:
    """Контроллер для работы с эндпоинтами /clients."""

    def __init__(self, request=None):
        self._client = APIClient(request)

    def list(self) -> list:
        """GET /clients/ — список всех клиентов."""
        return self._client.get('/clients/') or []

    def search(self, q: str) -> list:
        """GET /clients/search/?q=... — поиск по ФИО."""
        return self._client.get('/clients/search/', params={'q': q}) or []

    def get(self, client_id: int) -> dict:
        """GET /clients/{client_id}/"""
        return self._client.get(f'/clients/{client_id}/')

    def create(self, data: dict) -> dict:
        """POST /clients/"""
        return self._client.post('/clients/', data)

    def update(self, client_id: int, data: dict) -> dict:
        """PUT /clients/{client_id}/"""
        return self._client.put(f'/clients/{client_id}/', data)

    def delete(self, client_id: int) -> None:
        """DELETE /clients/{client_id}/"""
        self._client.delete(f'/clients/{client_id}/')

    def purge(self) -> tuple[int, int]:
        """
        Удалить всех клиентов по одному.
        Возвращает (deleted_count, error_count).
        """
        clients = self.list()
        deleted = 0
        errors = 0
        for c in clients:
            cid = c.get('id')
            if cid is None:
                continue
            try:
                self.delete(cid)
                deleted += 1
            except Exception:
                errors += 1
        return deleted, errors
