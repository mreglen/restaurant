"""
Views для управления заказами.
"""
from collections import defaultdict

from django.shortcuts import render, redirect
from django.contrib import messages
from core.api_client import APIClient
from core.permissions import ROLE_ADMIN, ROLE_MANAGER, require_session_roles


def order_list(request):
    """Список всех заказов."""
    client = APIClient(request)
    try:
        orders = client.get('/orders/')
    except Exception as e:
        messages.error(request, f'Ошибка загрузки: {str(e)}')
        orders = []

    return render(request, 'orders/list.html', {'orders': orders})


def order_detail(request, order_id):
    """Детальная информация о заказе."""
    client = APIClient(request)
    try:
        order = client.get(f'/orders/{order_id}/')
        dish_names = {}
        try:
            dishes = client.get('/dishes/')
            dish_names = {d['id']: d.get('name', '') for d in dishes}
        except Exception:
            pass
        return render(request, 'orders/detail.html', {
            'order': order,
            'dish_names': dish_names,
        })
    except Exception as e:
        messages.error(request, f'Ошибка: {str(e)}')
        return redirect('order_list')


def order_create(request):
    """Создание нового заказа."""
    client = APIClient(request)

    if request.method == 'POST':
        items = []
        index = 0
        while f'items[{index}][dish_id]' in request.POST:
            dish_id = request.POST.get(f'items[{index}][dish_id]')
            quantity = request.POST.get(f'items[{index}][quantity]')
            if dish_id and quantity:
                items.append({
                    'dish_id': int(dish_id),
                    'quantity': int(quantity),
                })
            index += 1

        data = {
            'table_number': int(request.POST.get('table_number')),
            'client_id': int(request.POST.get('client_id')) if request.POST.get('client_id') else None,
            'items': items,
        }

        try:
            client.post('/orders/', data)
            messages.success(request, 'Заказ успешно создан!')
            return redirect('order_list')
        except Exception as e:
            messages.error(request, f'Ошибка создания: {str(e)}')

    try:
        dishes = client.get('/dishes/')
        clients = client.get('/clients/')
    except Exception:
        dishes = []
        clients = []

    return render(request, 'orders/create.html', {
        'dishes': dishes,
        'clients': clients,
    })


@require_session_roles(ROLE_ADMIN, ROLE_MANAGER)
def order_update(request, order_id):
    """Обновление заказа."""
    client = APIClient(request)

    if request.method == 'POST':
        data = {
            'table_number': int(request.POST.get('table_number')),
            'client_id': int(request.POST.get('client_id')) if request.POST.get('client_id') else None,
        }

        try:
            client.put(f'/orders/{order_id}/', data)
            messages.success(request, 'Заказ обновлен!')
            return redirect('order_list')
        except Exception as e:
            messages.error(request, f'Ошибка обновления: {str(e)}')

    try:
        order = client.get(f'/orders/{order_id}/')
        clients = client.get('/clients/')
        return render(request, 'orders/update.html', {
            'order': order,
            'clients': clients,
        })
    except Exception as e:
        messages.error(request, f'Ошибка: {str(e)}')
        return redirect('order_list')


@require_session_roles(ROLE_ADMIN, ROLE_MANAGER)
def order_delete(request, order_id):
    """Удаление заказа."""
    try:
        client = APIClient(request)
        client.delete(f'/orders/{order_id}/')
        messages.success(request, 'Заказ удален!')
    except Exception as e:
        messages.error(request, f'Ошибка удаления: {str(e)}')

    return redirect('order_list')


@require_session_roles(ROLE_ADMIN, ROLE_MANAGER)
def order_statistics(request):
    """Агрегированная статистика по блюдам из списка заказов (без отдельного API)."""
    client = APIClient(request)
    try:
        orders = client.get('/orders/')
    except Exception as e:
        messages.error(request, f'Ошибка загрузки заказов: {str(e)}')
        orders = []

    dish_qty = defaultdict(int)
    dish_revenue = defaultdict(float)
    for order in orders or []:
        for item in order.get('items') or []:
            did = item.get('dish_id')
            if did is None:
                continue
            q = int(item.get('quantity') or 0)
            price = float(item.get('price') or 0)
            dish_qty[did] += q
            dish_revenue[did] += price * q

    dish_names = {}
    try:
        dishes = client.get('/dishes/')
        dish_names = {d['id']: d.get('name', '') for d in dishes}
    except Exception:
        pass

    rows = []
    for did in sorted(dish_qty.keys(), key=lambda x: dish_revenue[x], reverse=True):
        rows.append({
            'dish_id': did,
            'name': dish_names.get(did, f'Блюдо #{did}'),
            'quantity': dish_qty[did],
            'revenue': dish_revenue[did],
        })

    total_orders = len(orders) if isinstance(orders, list) else 0
    total_revenue = sum(dish_revenue.values())

    return render(request, 'orders/statistics.html', {
        'rows': rows,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
    })
