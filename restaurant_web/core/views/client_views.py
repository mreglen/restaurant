"""
Views для управления клиентами.
"""
from django.shortcuts import render, redirect
from django.contrib import messages
from core.api_client import APIClient
from core.permissions import (
    ROLE_ADMIN,
    ROLE_MANAGER,
    require_session_roles,
)


def client_list(request):
    """Список клиентов или поиск по ФИО (GET /clients/search/)."""
    client = APIClient(request)
    q = (request.GET.get('q') or request.GET.get('search') or '').strip()
    try:
        if q:
            clients = client.get('/clients/search/', params={'q': q})
        else:
            clients = client.get('/clients/')
    except Exception as e:
        messages.error(request, f'Ошибка загрузки клиентов: {str(e)}')
        clients = []

    return render(request, 'clients/list.html', {
        'clients': clients,
        'search_q': q,
    })


def client_detail(request, client_id):
    """Детальная информация о клиенте."""
    client = APIClient(request)
    try:
        client_data = client.get(f'/clients/{client_id}/')
        return render(request, 'clients/detail.html', {'client': client_data})
    except Exception as e:
        messages.error(request, f'Ошибка: {str(e)}')
        return redirect('client_list')


@require_session_roles(ROLE_ADMIN, ROLE_MANAGER)
def client_create(request):
    """Создание нового клиента."""
    if request.method == 'POST':
        data = {
            'last_name': request.POST.get('last_name', '').strip(),
            'first_name': request.POST.get('first_name', '').strip(),
            'patronymic': (request.POST.get('patronymic') or '').strip(),
            'phone': request.POST.get('phone'),
            'is_vip': request.POST.get('is_vip') == 'on',
            'bonus_points': int(request.POST.get('bonus_points', 0)),
        }

        try:
            client = APIClient(request)
            client.post('/clients/', data)
            messages.success(request, 'Клиент успешно создан!')
            return redirect('client_list')
        except Exception as e:
            messages.error(request, f'Ошибка создания клиента: {str(e)}')

    return render(request, 'clients/create.html')


@require_session_roles(ROLE_ADMIN, ROLE_MANAGER)
def client_update(request, client_id):
    """Обновление данных клиента."""
    client = APIClient(request)

    if request.method == 'POST':
        data = {
            'last_name': request.POST.get('last_name', '').strip(),
            'first_name': request.POST.get('first_name', '').strip(),
            'patronymic': (request.POST.get('patronymic') or '').strip(),
            'phone': request.POST.get('phone'),
            'is_vip': request.POST.get('is_vip') == 'on',
            'bonus_points': int(request.POST.get('bonus_points', 0)),
        }

        try:
            client.put(f'/clients/{client_id}/', data)
            messages.success(request, 'Данные клиента обновлены!')
            return redirect('client_list')
        except Exception as e:
            messages.error(request, f'Ошибка обновления: {str(e)}')

    try:
        client_data = client.get(f'/clients/{client_id}/')
        return render(request, 'clients/update.html', {'client': client_data})
    except Exception as e:
        messages.error(request, f'Ошибка: {str(e)}')
        return redirect('client_list')


@require_session_roles(ROLE_ADMIN, ROLE_MANAGER)
def client_delete(request, client_id):
    """Удаление клиента."""
    try:
        client = APIClient(request)
        client.delete(f'/clients/{client_id}/')
        messages.success(request, 'Клиент удален!')
    except Exception as e:
        messages.error(request, f'Ошибка удаления: {str(e)}')

    return redirect('client_list')


@require_session_roles(ROLE_ADMIN)
def client_purge(request):
    """
    Массовое удаление всех клиентов (только администратор).
    GET — форма подтверждения; POST — удаление по одному через API.
    """
    client = APIClient(request)

    if request.method == 'POST':
        if request.POST.get('confirm_text', '').strip() != 'УДАЛИТЬ ВСЕХ':
            messages.error(request, 'Неверная фраза подтверждения. Введите ровно: УДАЛИТЬ ВСЕХ')
            return redirect('client_purge')

        try:
            clients = client.get('/clients/')
        except Exception as e:
            messages.error(request, f'Не удалось получить список клиентов: {str(e)}')
            return redirect('client_purge')

        deleted = 0
        errors = 0
        for c in clients:
            cid = c.get('id')
            if cid is None:
                continue
            try:
                client.delete(f'/clients/{cid}/')
                deleted += 1
            except Exception:
                errors += 1

        messages.success(request, f'Удалено записей: {deleted}. Ошибок: {errors}.')
        return redirect('client_list')

    try:
        clients = client.get('/clients/')
        count = len(clients) if isinstance(clients, list) else 0
    except Exception as e:
        messages.error(request, f'Ошибка загрузки: {str(e)}')
        count = 0

    return render(request, 'clients/purge.html', {'client_count': count})
