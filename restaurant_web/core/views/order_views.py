"""
Views для управления заказами.
"""
from collections import defaultdict

from django.shortcuts import render, redirect
from django.contrib import messages
from core.controllers.order_controller import OrderController
from core.controllers.dish_controller import DishController
from core.controllers.client_controller import ClientController
from core.permissions import ROLE_ADMIN, ROLE_MANAGER, require_session_roles


def order_list(request):
    """Список всех заказов."""
    try:
        orders = OrderController(request).list()
    except Exception as e:
        messages.error(request, f'Ошибка загрузки: {str(e)}')
        orders = []

    return render(request, 'orders/list.html', {'orders': orders})


def order_detail(request, order_id):
    """Детальная информация о заказе."""
    order_ctrl = OrderController(request)
    dish_ctrl = DishController(request)
    try:
        order = order_ctrl.get(order_id)
        dish_names = {}
        try:
            dishes = dish_ctrl.list()
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
    order_ctrl = OrderController(request)
    dish_ctrl = DishController(request)
    client_ctrl = ClientController(request)

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
            order_ctrl.create(data)
            messages.success(request, 'Заказ успешно создан!')
            return redirect('order_list')
        except Exception as e:
            messages.error(request, f'Ошибка создания: {str(e)}')

    try:
        dishes = dish_ctrl.list()
        clients = client_ctrl.list()
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
    order_ctrl = OrderController(request)
    client_ctrl = ClientController(request)

    if request.method == 'POST':
        data = {
            'table_number': int(request.POST.get('table_number')),
            'client_id': int(request.POST.get('client_id')) if request.POST.get('client_id') else None,
        }
        try:
            order_ctrl.update(order_id, data)
            messages.success(request, 'Заказ обновлен!')
            return redirect('order_list')
        except Exception as e:
            messages.error(request, f'Ошибка обновления: {str(e)}')

    try:
        order = order_ctrl.get(order_id)
        clients = client_ctrl.list()
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
        OrderController(request).delete(order_id)
        messages.success(request, 'Заказ удален!')
    except Exception as e:
        messages.error(request, f'Ошибка удаления: {str(e)}')

    return redirect('order_list')


@require_session_roles(ROLE_ADMIN, ROLE_MANAGER)
def order_statistics(request):
    """Агрегированная статистика по блюдам из списка заказов."""
    order_ctrl = OrderController(request)
    dish_ctrl = DishController(request)

    try:
        orders = order_ctrl.list()
    except Exception as e:
        messages.error(request, f'Ошибка загрузки заказов: {str(e)}')
        orders = []

    dish_qty: dict[int, int] = defaultdict(int)
    dish_revenue: dict[int, float] = defaultdict(float)
    for order in orders or []:
        for item in order.get('items') or []:
            did = item.get('dish_id')
            if did is None:
                continue
            q = int(item.get('quantity') or 0)
            price = float(item.get('price') or 0)
            dish_qty[did] += q
            dish_revenue[did] += price * q

    dish_names: dict[int, str] = {}
    try:
        dishes = dish_ctrl.list()
        dish_names = {d['id']: d.get('name', '') for d in dishes}
    except Exception:
        pass

    rows = [
        {
            'dish_id': did,
            'name': dish_names.get(did, f'Блюдо #{did}'),
            'quantity': dish_qty[did],
            'revenue': dish_revenue[did],
        }
        for did in sorted(dish_qty, key=lambda x: dish_revenue[x], reverse=True)
    ]

    total_orders = len(orders)
    total_revenue = sum(dish_revenue.values())
    average_check = total_revenue / total_orders if total_orders else 0

    return render(request, 'orders/statistics.html', {
        'stats': {
            'total_orders': total_orders,
            'total_revenue': total_revenue,
            'average_check': average_check,
            'popular_dishes': [
                {'name': r['name'], 'count': r['quantity'], 'revenue': r['revenue']}
                for r in rows
            ],
        },
    })
