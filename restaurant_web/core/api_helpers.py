"""
Вспомогательные функции для запросов к Restaurant API из Django views.
"""
from __future__ import annotations

from core.api_client import APIClient


def anonymous_api_client() -> APIClient:
    """Клиент без JWT для публичных эндпоинтов."""
    client = APIClient()
    client.session.headers.pop('Authorization', None)
    return client


def ensure_list(data) -> list:
    return data if isinstance(data, list) else []


def fetch_list(client: APIClient, endpoint: str) -> tuple[list, str | None]:
    try:
        return ensure_list(client.get(endpoint)), None
    except Exception as exc:
        return [], str(exc)


def menu_dish_ids(menu: dict) -> list[int]:
    """ID блюд в меню (API v2: dish_ids; совместимость со старым items)."""
    if not isinstance(menu, dict):
        return []
    raw = menu.get('dish_ids')
    if raw is None:
        raw = menu.get('items') or menu.get('dishes') or []
    return [int(x) for x in raw if x is not None]


def menu_dishes_for(menu: dict, dishes_dict: dict) -> list[dict]:
    return [dishes_dict[did] for did in menu_dish_ids(menu) if did in dishes_dict]
