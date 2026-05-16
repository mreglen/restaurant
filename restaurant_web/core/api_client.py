"""
API клиент для взаимодействия с Restaurant API.
Использует библиотеку requests для отправки HTTP запросов.
"""
import requests
from django.conf import settings
from django.contrib import messages


class APIClient:
    """
    Клиент для работы с Restaurant API.
    Поддерживает все HTTP методы и автоматическую обработку JWT токенов.
    """
    
    def __init__(self, request=None):
        """
        Инициализация API клиента.
        
        Args:
            request: Django request объект (для доступа к сессии и сообщениям)
        """
        self.base_url = settings.API_BASE_URL
        self.request = request
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        })
        
        # Добавляем токен из сессии если есть
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
        
        Args:
            response: Response объект от requests
            
        Returns:
            dict: JSON данные ответа
            
        Raises:
            Exception: При ошибке API
        """
        if response.status_code in [200, 201]:
            try:
                return response.json()
            except:
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
            except:
                raise Exception(f'Ошибка API: {response.status_code}')
    
    def get(self, endpoint, params=None):
        """
        GET запрос к API.
        
        Args:
            endpoint: URL endpoint (например, '/clients/')
            params: Параметры запроса (dict)
            
        Returns:
            dict: JSON данные ответа
        """
        url = f"{self.base_url}{endpoint}"
        response = self.session.get(url, params=params)
        return self._handle_response(response)
    
    def post(self, endpoint, data=None):
        """
        POST запрос к API.
        
        Args:
            endpoint: URL endpoint
            data: Данные для отправки (dict)
            
        Returns:
            dict: JSON данные ответа
        """
        url = f"{self.base_url}{endpoint}"
        response = self.session.post(url, json=data)
        return self._handle_response(response)

    def post_form(self, endpoint, data=None):
        """
        POST с телом application/x-www-form-urlencoded (например /auth/login/ в FastAPI v2).
        """
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
        """
        PUT запрос к API.
        
        Args:
            endpoint: URL endpoint
            data: Данные для отправки (dict)
            
        Returns:
            dict: JSON данные ответа
        """
        url = f"{self.base_url}{endpoint}"
        response = self.session.put(url, json=data)
        return self._handle_response(response)
    
    def delete(self, endpoint):
        """
        DELETE запрос к API.
        
        Args:
            endpoint: URL endpoint
            
        Returns:
            dict: JSON данные ответа
        """
        url = f"{self.base_url}{endpoint}"
        response = self.session.delete(url)
        return self._handle_response(response)
