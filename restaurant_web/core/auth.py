"""
Система аутентификации для работы с JWT токенами.
"""
import jwt
from django.conf import settings

from core.controllers.auth_controller import AuthController
from core.controllers.base import APIClient


def _store_role_from_token(request, access_token: str) -> None:
    """Декодирует JWT и сохраняет role_id в сессии."""
    secret = getattr(settings, 'API_JWT_SECRET', '') or ''
    if not secret:
        return
    algo = getattr(settings, 'API_JWT_ALGORITHM', 'HS256')
    try:
        payload = jwt.decode(
            access_token,
            secret,
            algorithms=[algo],
            options={'verify_signature': True},
        )
        rid = payload.get('role_id')
        if rid is not None:
            request.session['role_id'] = int(rid)
    except (jwt.PyJWTError, TypeError, ValueError):
        request.session.pop('role_id', None)


def backfill_role_id_if_missing(request) -> None:
    """Для старых сессий без role_id после включения API_JWT_SECRET."""
    if 'access_token' not in request.session or request.session.get('role_id') is not None:
        return
    _store_role_from_token(request, request.session['access_token'])


def login_user(username: str, password: str, request) -> dict:
    """
    Аутентификация пользователя через API.
    FastAPI v2 /auth/login принимает form-urlencoded, не JSON.
    """
    controller = AuthController(request)
    response = controller.login(username, password)

    if response and 'access_token' in response:
        request.session['access_token'] = response['access_token']
        request.session['username'] = username
        _store_role_from_token(request, response['access_token'])
        return response

    raise Exception('Неверные учетные данные')


def register_user(
    last_name: str,
    first_name: str,
    patronymic: str,
    role,
    phone,
    username: str,
    password: str,
    request,
) -> dict:
    """Регистрация нового пользователя через API."""
    controller = AuthController(request)
    data = {
        'last_name': last_name,
        'first_name': first_name,
        'patronymic': patronymic or '',
        'role': role,
        'phone': phone or None,
        'username': username,
        'password': password,
    }
    response = controller.register(data)

    if response and 'access_token' in response:
        request.session['access_token'] = response['access_token']
        request.session['username'] = username
        _store_role_from_token(request, response['access_token'])
        return response

    raise Exception('Ошибка регистрации')


def logout_user(request) -> None:
    """Выход пользователя из системы."""
    for key in ('access_token', 'username', 'role_id'):
        request.session.pop(key, None)


def get_current_user(request) -> dict | None:
    """Получение информации о текущем пользователе из сессии."""
    if 'access_token' not in request.session:
        return None
    try:
        return {
            'username': request.session.get('username'),
            'role_id': request.session.get('role_id'),
        }
    except Exception:
        return None


def is_authenticated(request) -> bool:
    """Проверка, авторизован ли пользователь."""
    return 'access_token' in request.session
