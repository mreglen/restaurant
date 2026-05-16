"""
Views для управления сотрудниками.
"""
from django.shortcuts import render, redirect
from django.contrib import messages
from core.api_client import APIClient
from core.permissions import (
    ROLE_ADMIN,
    can_view_employees,
    require_session_roles,
    role_id_from_session,
    REGISTRATION_ROLE_CHOICES,
)


def employee_list(request):
    """Список сотрудников или поиск по ФИО."""
    rid = role_id_from_session(request.session)
    if not can_view_employees(rid):
        messages.warning(request, 'Недостаточно прав.')
        return redirect('dashboard')

    client = APIClient(request)
    q = (request.GET.get('q') or '').strip()
    try:
        if q:
            employees = client.get('/employees/search/', params={'q': q})
        else:
            employees = client.get('/employees/')
        if rid == ROLE_ADMIN:
            roles = client.get('/roles/')
            roles_dict = {r['id']: r['name'] for r in roles}
        else:
            roles_dict = {r['id']: r['name'] for r in REGISTRATION_ROLE_CHOICES}
    except Exception as e:
        messages.error(request, f'Ошибка загрузки: {str(e)}')
        employees = []
        roles_dict = {}

    return render(request, 'employees/list.html', {
        'employees': employees,
        'roles_dict': roles_dict,
        'search_q': q,
    })


def employee_detail(request, employee_id):
    """Детальная информация о сотруднике."""
    rid = role_id_from_session(request.session)
    if not can_view_employees(rid):
        messages.warning(request, 'Недостаточно прав.')
        return redirect('dashboard')

    client = APIClient(request)
    try:
        employee = client.get(f'/employees/{employee_id}/')
        return render(request, 'employees/detail.html', {'employee': employee})
    except Exception as e:
        messages.error(request, f'Ошибка: {str(e)}')
        return redirect('employee_list')


@require_session_roles(ROLE_ADMIN)
def employee_create(request):
    """Создание нового сотрудника."""
    client = APIClient(request)

    if request.method == 'POST':
        data = {
            'last_name': request.POST.get('last_name', '').strip(),
            'first_name': request.POST.get('first_name', '').strip(),
            'patronymic': (request.POST.get('patronymic') or '').strip(),
            'role_id': int(request.POST.get('role_id')),
            'phone': request.POST.get('phone'),
            'username': request.POST.get('username'),
            'password': request.POST.get('password'),
        }

        try:
            client.post('/employees/', data)
            messages.success(request, 'Сотрудник успешно создан!')
            return redirect('employee_list')
        except Exception as e:
            messages.error(request, f'Ошибка создания: {str(e)}')

    try:
        roles = client.get('/roles/')
    except Exception:
        roles = []

    return render(request, 'employees/create.html', {'roles': roles})


@require_session_roles(ROLE_ADMIN)
def employee_update(request, employee_id):
    """Обновление данных сотрудника."""
    client = APIClient(request)

    if request.method == 'POST':
        data = {
            'last_name': request.POST.get('last_name', '').strip(),
            'first_name': request.POST.get('first_name', '').strip(),
            'patronymic': (request.POST.get('patronymic') or '').strip(),
            'role_id': int(request.POST.get('role_id')),
            'phone': request.POST.get('phone'),
        }

        try:
            client.put(f'/employees/{employee_id}/', data)
            messages.success(request, 'Данные сотрудника обновлены!')
            return redirect('employee_list')
        except Exception as e:
            messages.error(request, f'Ошибка обновления: {str(e)}')

    try:
        employee = client.get(f'/employees/{employee_id}/')
        roles = client.get('/roles/')
        return render(request, 'employees/update.html', {
            'employee': employee,
            'roles': roles,
        })
    except Exception as e:
        messages.error(request, f'Ошибка: {str(e)}')
        return redirect('employee_list')


@require_session_roles(ROLE_ADMIN)
def employee_delete(request, employee_id):
    """Удаление сотрудника."""
    try:
        client = APIClient(request)
        client.delete(f'/employees/{employee_id}/')
        messages.success(request, 'Сотрудник удален!')
    except Exception as e:
        messages.error(request, f'Ошибка удаления: {str(e)}')

    return redirect('employee_list')
