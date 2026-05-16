"""
Context processors для Jinja2 шаблонов.
"""
from types import SimpleNamespace

from django.middleware.csrf import get_token

from core.permissions import permissions_dict, role_id_from_session


def csrf_processor(request):
    """
    Добавляет CSRF токен в контекст для Jinja2 шаблонов.

    Args:
        request: Django request объект

    Returns:
        dict: CSRF токен
    """
    rid = role_id_from_session(request.session) if request.session else None
    return {
        'csrf_token': get_token(request),
        'request': request,
        'perms': SimpleNamespace(**permissions_dict(rid)),
    }
