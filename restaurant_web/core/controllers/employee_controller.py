"""
Контроллер сотрудников — CRUD + поиск.
"""
from core.controllers.base import APIClient


class EmployeeController:
    """Контроллер для работы с эндпоинтами /employees."""

    def __init__(self, request=None):
        self._client = APIClient(request)

    def list(self) -> list:
        """GET /employees/ — список всех сотрудников."""
        return self._client.get('/employees/') or []

    def search(self, q: str) -> list:
        """GET /employees/search/?q=... — поиск по ФИО."""
        return self._client.get('/employees/search/', params={'q': q}) or []

    def get(self, employee_id: int) -> dict:
        """GET /employees/{employee_id}/"""
        return self._client.get(f'/employees/{employee_id}/')

    def create(self, data: dict) -> dict:
        """POST /employees/"""
        return self._client.post('/employees/', data)

    def update(self, employee_id: int, data: dict) -> dict:
        """PUT /employees/{employee_id}/"""
        return self._client.put(f'/employees/{employee_id}/', data)

    def delete(self, employee_id: int) -> None:
        """DELETE /employees/{employee_id}/"""
        self._client.delete(f'/employees/{employee_id}/')
