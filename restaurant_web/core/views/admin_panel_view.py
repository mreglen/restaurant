"""
Админ-панель: сводка, статистика и превью списков через API.
"""
from django.contrib import messages
from django.shortcuts import render

from core.controllers.base import APIClient
from core.permissions import ROLE_ADMIN, require_session_roles

_PREVIEW = 8

_RESOURCE_LABELS = {
    'clients': 'Клиенты',
    'orders': 'Заказы',
    'dishes': 'Блюда',
    'menus': 'Меню',
    'ingredients': 'Ингредиенты',
    'tables': 'Столики',
    'employees': 'Сотрудники',
    'roles': 'Роли',
}


def _fetch_list(client: APIClient, endpoint: str, key: str) -> tuple[list, str | None]:
    label = _RESOURCE_LABELS.get(key, key)
    try:
        data = client.get(endpoint)
        if isinstance(data, list):
            return data, None
        return [], f'{label}: неверный формат ответа API'
    except Exception as exc:
        return [], f'{label}: {exc}'


def _order_items_count(order: dict) -> int:
    items = order.get('items') or []
    return sum(int(item.get('quantity') or 0) for item in items)


@require_session_roles(ROLE_ADMIN)
def admin_panel_view(request):
    """Панель администратора: счётчики, статистика, превью и быстрые действия."""
    client = APIClient(request)
    fetch_errors: list[str] = []

    def load(key: str, endpoint: str) -> list:
        items, error = _fetch_list(client, endpoint, key)
        if error:
            fetch_errors.append(error)
        return items

    clients = load('clients', '/clients/')
    orders = load('orders', '/orders/')
    dishes = load('dishes', '/dishes/')
    menus = load('menus', '/menus/')
    ingredients = load('ingredients', '/ingredients/')
    tables = load('tables', '/tables/')
    employees = load('employees', '/employees/')
    roles = load('roles', '/roles/')

    for error in fetch_errors:
        messages.warning(request, error)

    roles_dict = {
        r['id']: r.get('name', f'Роль #{r["id"]}')
        for r in roles
        if isinstance(r, dict) and 'id' in r
    }
    employees_dict = {
        e['id']: ' '.join(
            p for p in (e.get('last_name'), e.get('first_name')) if p
        ).strip() or e.get('username', f'#{e["id"]}')
        for e in employees
        if isinstance(e, dict) and 'id' in e
    }

    total_revenue = sum(float(o.get('total_price') or 0) for o in orders)
    total_order_items = sum(_order_items_count(o) for o in orders)
    vip_clients = sum(1 for c in clients if c.get('is_vip'))
    recent_orders = sorted(orders, key=lambda o: o.get('id', 0), reverse=True)[:_PREVIEW]

    return render(
        request,
        'admin_panel.html',
        {
            'clients_preview': clients[:_PREVIEW],
            'clients_count': len(clients),
            'vip_clients_count': vip_clients,
            'orders_preview': recent_orders,
            'orders_count': len(orders),
            'total_revenue': total_revenue,
            'total_order_items': total_order_items,
            'dishes_preview': dishes[:_PREVIEW],
            'dishes_count': len(dishes),
            'employees_preview': employees[:_PREVIEW],
            'employees_count': len(employees),
            'menus_preview': menus[:_PREVIEW],
            'menus_count': len(menus),
            'ingredients_preview': ingredients[:_PREVIEW],
            'ingredients_count': len(ingredients),
            'roles_preview': roles[:_PREVIEW],
            'roles_count': len(roles),
            'tables_preview': tables[:_PREVIEW],
            'tables_count': len(tables),
            'roles_dict': roles_dict,
            'employees_dict': employees_dict,
            'fetch_errors': fetch_errors,
        },
    )
