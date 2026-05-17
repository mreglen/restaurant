"""
Контроллер меню — CRUD + поиск + экспорт DOCX/XLSX.
"""
from django.conf import settings

from core.controllers.base import APIClient


class MenuController:
    """Контроллер для работы с эндпоинтами /menus."""

    def __init__(self, request=None):
        self._client = APIClient(request)
        self._request = request

    def list(self) -> list:
        """GET /menus/ — список всех меню."""
        return self._client.get('/menus/') or []

    def search(self, q: str) -> list:
        """GET /menus/search/?q=... — поиск по названию."""
        return self._client.get('/menus/search/', params={'q': q}) or []

    def get(self, menu_id: int) -> dict:
        """GET /menus/{menu_id}/"""
        return self._client.get(f'/menus/{menu_id}/')

    def create(self, data: dict) -> dict:
        """POST /menus/"""
        return self._client.post('/menus/', data)

    def update(self, menu_id: int, data: dict) -> dict:
        """PUT /menus/{menu_id}/"""
        return self._client.put(f'/menus/{menu_id}/', data)

    def delete(self, menu_id: int) -> None:
        """DELETE /menus/{menu_id}/"""
        self._client.delete(f'/menus/{menu_id}/')

    def export_docx(self, menu_id: int):
        """
        GET /menus/{menu_id}/export/docx — бинарный поток.
        Возвращает объект requests.Response с содержимым файла.
        """
        return self._client.get_raw(f'/menus/{menu_id}/export/docx')

    def export_xlsx(self, menu_id: int):
        """
        GET /menus/{menu_id}/export/xlsx — бинарный поток.
        Возвращает объект requests.Response с содержимым файла.
        """
        return self._client.get_raw(f'/menus/{menu_id}/export/xlsx')
