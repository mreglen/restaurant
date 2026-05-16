"""
Dashboard view — панель управления для авторизованных сотрудников.
"""
from django.contrib import messages
from django.shortcuts import render

from core.api_client import APIClient
from core.api_helpers import fetch_list
from core.permissions import ROLE_ADMIN, can_view_employees, role_id_from_session


def dashboard_view(request):
    """Главная страница с обзором ресторана."""
    client = APIClient(request)
    rid = role_id_from_session(request.session)

    clients, err = fetch_list(client, '/clients/')
    if err:
        messages.warning(request, f'Клиенты: {err}')
    orders, err = fetch_list(client, '/orders/')
    if err:
        messages.warning(request, f'Заказы: {err}')
    dishes, err = fetch_list(client, '/dishes/')
    if err:
        messages.warning(request, f'Блюда: {err}')

    employees = []
    if can_view_employees(rid):
        employees, err = fetch_list(client, '/employees/')
        if err:
            messages.warning(request, f'Сотрудники: {err}')

    recent_orders = sorted(orders, key=lambda o: o.get('id', 0), reverse=True)[:5]
    total_revenue = sum(float(o.get('total_price') or 0) for o in orders)

    return render(request, 'dashboard.html', {
        'clients': clients,
        'orders': orders,
        'recent_orders': recent_orders,
        'dishes': dishes,
        'employees': employees,
        'total_revenue': total_revenue,
        'is_admin': rid == ROLE_ADMIN,
    })
