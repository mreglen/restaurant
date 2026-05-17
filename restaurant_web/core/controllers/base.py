"""
Базовый HTTP-клиент для взаимодействия с Restaurant API.
Использует библиотеку requests для отправки HTTP запросов.
"""
import requests
from django.conf import settings


class APIClient:
    """
    Клиент для работы с Restaurant API.
    Поддерживает все HTTP методы и автоматическую обработку JWT токенов.
    """

    def __init__(self, request=None):
        self.base_url = settings.API_BASE_URL
        self.request = request
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        })

        if request and 'access_token' in request.session:
            self.set_token(request.session['access_token'])

    def set_token(self, token):
        """Установить JWT токен для авторизации."""
        self.session.headers.update({
            'Authorization': f'Bearer {token}'
        })

    def _handle_response(self, response):
        """
        Обработка ответа от API.
        Возвращает JSON-данные или None при пустом теле ответа (204).
        """
        if response.status_code in (200, 201, 204):
            if response.status_code == 204 or not response.content:
                return None
            try:
                return response.json()
            except Exception:
                return None
        elif response.status_code == 401:
            raise Exception('Необходима авторизация')
        elif response.status_code == 403:
            raise Exception('Доступ запрещен')
        elif response.status_code == 404:
            raise Exception('Ресурс не найден')
        else:
            try:
                error_data = response.json()
                error_msg = error_data.get('detail', str(error_data))
                if isinstance(error_data, dict):
                    errors = []
                    for key, value in error_data.items():
                        if isinstance(value, list):
                            errors.append(f'{key}: {", ".join(str(v) for v in value)}')
                        else:
                            errors.append(f'{key}: {value}')
                    if errors:
                        error_msg = '; '.join(errors)
                raise Exception(error_msg)
            except Exception:
                raise Exception(f'Ошибка API: {response.status_code}')

    def get(self, endpoint, params=None):
        """GET запрос к API."""
        url = f"{self.base_url}{endpoint}"
        response = self.session.get(url, params=params)
        return self._handle_response(response)

    def post(self, endpoint, data=None):
        """POST запрос к API (JSON)."""
        url = f"{self.base_url}{endpoint}"
        response = self.session.post(url, json=data)
        return self._handle_response(response)

    def post_form(self, endpoint, data=None):
        """POST с телом application/x-www-form-urlencoded."""
        url = f"{self.base_url}{endpoint}"
        headers = {
            k: v for k, v in self.session.headers.items()
            if k.lower() not in ('content-type', 'accept')
        }
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
        headers['Accept'] = 'application/json'
        response = self.session.post(url, data=data or {}, headers=headers)
        return self._handle_response(response)

    def put(self, endpoint, data=None):
        """PUT запрос к API."""
        url = f"{self.base_url}{endpoint}"
        response = self.session.put(url, json=data)
        return self._handle_response(response)

    def delete(self, endpoint):
        """DELETE запрос к API."""
        url = f"{self.base_url}{endpoint}"
        response = self.session.delete(url)
        return self._handle_response(response)

    def get_raw(self, endpoint, params=None):
        """GET запрос без обработки ответа (для бинарных данных)."""
        url = f"{self.base_url}{endpoint}"
        return self.session.get(url, params=params)
