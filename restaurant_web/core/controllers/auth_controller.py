"""
Контроллер аутентификации — login и register через API.
"""
from core.controllers.base import APIClient


class AuthController:
    """Контроллер для работы с эндпоинтами /auth."""

    def __init__(self, request=None):
        self._client = APIClient(request)
        self._client.session.headers.pop('Authorization', None)

    def login(self, username: str, password: str) -> dict:
        """
        POST /auth/login (form-urlencoded).
        Возвращает словарь с access_token.
        """
        return self._client.post_form(
            '/auth/login',
            {'username': username, 'password': password},
        )

    def register(self, data: dict) -> dict:
        """
        POST /auth/register (JSON).
        data: last_name, first_name, patronymic, role, phone, username, password
        """
        return self._client.post('/auth/register', data)
