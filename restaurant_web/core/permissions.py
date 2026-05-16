"""
Права веб-интерфейса по role_id из JWT (синхронно с restaurant_api v2).
"""
from __future__ import annotations

from typing import Any

ROLE_ADMIN = 1
ROLE_MANAGER = 2
ROLE_WAITER = 3


def role_id_from_session(session: dict) -> int | None:
    rid = session.get('role_id')
    if rid is None:
        return None
    try:
        return int(rid)
    except (TypeError, ValueError):
        return None


def is_admin(role_id: int | None) -> bool:
    return role_id == ROLE_ADMIN


def is_manager(role_id: int | None) -> bool:
    return role_id == ROLE_MANAGER


def is_waiter(role_id: int | None) -> bool:
    return role_id == ROLE_WAITER


def manager_or_admin(role_id: int | None) -> bool:
    return role_id in (ROLE_ADMIN, ROLE_MANAGER)


def can_view_employees(role_id: int | None) -> bool:
    return manager_or_admin(role_id)


def can_manage_employees(role_id: int | None) -> bool:
    return role_id == ROLE_ADMIN


def can_manage_roles(role_id: int | None) -> bool:
    return role_id == ROLE_ADMIN


def can_manage_clients(role_id: int | None) -> bool:
    return manager_or_admin(role_id)


def can_manage_dishes(role_id: int | None) -> bool:
    return manager_or_admin(role_id)


def can_manage_ingredients(role_id: int | None) -> bool:
    return manager_or_admin(role_id)


def can_manage_menus(role_id: int | None) -> bool:
    return manager_or_admin(role_id)


def can_export_menu_files(role_id: int | None) -> bool:
    return manager_or_admin(role_id)


def can_create_order(role_id: int | None) -> bool:
    """По API создать заказ может любой авторизованный пользователь."""
    return True


def can_edit_or_delete_order(role_id: int | None) -> bool:
    return manager_or_admin(role_id)


def can_manage_tables(role_id: int | None) -> bool:
    return manager_or_admin(role_id)


def can_view_tables(role_id: int | None) -> bool:
    """По API список назначений столов доступен любому с токеном."""
    return True


def can_view_order_statistics(role_id: int | None) -> bool:
    return manager_or_admin(role_id)


def can_purge_all_clients(role_id: int | None) -> bool:
    return role_id == ROLE_ADMIN


# Синхронизировать с таблицей roles в БД API (гостевой GET /roles/ недоступен).
REGISTRATION_ROLE_CHOICES = [
    {'id': ROLE_ADMIN, 'name': 'Администратор'},
    {'id': ROLE_MANAGER, 'name': 'Менеджер'},
    {'id': ROLE_WAITER, 'name': 'Официант'},
]


def permissions_dict(role_id: int | None) -> dict[str, Any]:
    return {
        'role_id': role_id,
        'is_admin': is_admin(role_id),
        'is_manager': is_manager(role_id),
        'is_waiter': is_waiter(role_id),
        'can_view_employees': can_view_employees(role_id),
        'can_manage_employees': can_manage_employees(role_id),
        'can_manage_roles': can_manage_roles(role_id),
        'can_manage_clients': can_manage_clients(role_id),
        'can_manage_dishes': can_manage_dishes(role_id),
        'can_manage_ingredients': can_manage_ingredients(role_id),
        'can_manage_menus': can_manage_menus(role_id),
        'can_export_menu_files': can_export_menu_files(role_id),
        'can_create_order': can_create_order(role_id),
        'can_edit_or_delete_order': can_edit_or_delete_order(role_id),
        'can_manage_tables': can_manage_tables(role_id),
        'can_view_tables': can_view_tables(role_id),
        'can_view_order_statistics': can_view_order_statistics(role_id),
        'can_purge_all_clients': can_purge_all_clients(role_id),
    }


def require_session_roles(*allowed_role_ids: int):
    """Ограничение view по role_id из сессии (до запроса к API)."""
    from functools import wraps

    from django.contrib import messages
    from django.shortcuts import redirect

    allowed = set(allowed_role_ids)

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            rid = role_id_from_session(request.session)
            if rid not in allowed:
                messages.warning(request, 'Недостаточно прав.')
                return redirect('dashboard')
            return view_func(request, *args, **kwargs)

        return _wrapped

    return decorator
