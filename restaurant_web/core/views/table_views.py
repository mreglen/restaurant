"""
Views для управления закреплением столиков.
"""
from django.shortcuts import render, redirect
from django.contrib import messages
from core.api_client import APIClient
from core.permissions import (
    ROLE_ADMIN,
    ROLE_MANAGER,
    can_view_employees,
    require_session_roles,
    role_id_from_session,
)


def _employee_display_name(e: dict) -> str:
    """Собирает ФИО из полей API (обратная совместимость с full_name)."""
    if 'full_name' in e and e.get('full_name'):
        return e['full_name']
    parts = [e.get('last_name'), e.get('first_name'), e.get('patronymic') or '']
    return ' '.join(p for p in parts if p).strip() or str(e.get('id', ''))


def table_list(request):
    """Список всех закрепленных столиков."""
    client = APIClient(request)
    rid = role_id_from_session(request.session)
    employees_dict = {}
    try:
        tables = client.get('/tables/')
    except Exception as e:
        messages.error(request, f'Ошибка загрузки: {str(e)}')
        tables = []

    if can_view_employees(rid):
        try:
            employees = client.get('/employees/')
            employees_dict = {e['id']: _employee_display_name(e) for e in employees}
        except Exception:
            employees_dict = {}

    return render(request, 'tables/list.html', {
        'tables': tables,
        'employees_dict': employees_dict,
    })


def table_detail(request, assignment_id):
    """Детальная информация о назначении столика."""
    client = APIClient(request)
    rid = role_id_from_session(request.session)
    employees_dict = {}
    try:
        table = client.get(f'/tables/{assignment_id}/')
        if can_view_employees(rid):
            employees = client.get('/employees/')
            employees_dict = {e['id']: _employee_display_name(e) for e in employees}
        return render(request, 'tables/detail.html', {
            'table': table,
            'employees_dict': employees_dict,
        })
    except Exception as e:
        messages.error(request, f'Ошибка: {str(e)}')
        return redirect('table_list')


@require_session_roles(ROLE_ADMIN, ROLE_MANAGER)
def table_create(request):
    """Закрепление столика за сотрудником."""
    client = APIClient(request)

    if request.method == 'POST':
        data = {
            'table_number': int(request.POST.get('table_number')),
            'employee_id': int(request.POST.get('employee_id')),
        }

        try:
            client.post('/tables/', data)
            messages.success(request, 'Столик успешно закреплен!')
            return redirect('table_list')
        except Exception as e:
            messages.error(request, f'Ошибка закрепления: {str(e)}')

    try:
        employees = client.get('/employees/')
    except Exception:
        employees = []

    return render(request, 'tables/create.html', {'employees': employees})


@require_session_roles(ROLE_ADMIN, ROLE_MANAGER)
def table_update(request, assignment_id):
    """Обновление назначения столика."""
    client = APIClient(request)

    if request.method == 'POST':
        data = {
            'table_number': int(request.POST.get('table_number')),
            'employee_id': int(request.POST.get('employee_id')),
        }

        try:
            client.put(f'/tables/{assignment_id}/', data)
            messages.success(request, 'Назначение столика обновлено!')
            return redirect('table_list')
        except Exception as e:
            messages.error(request, f'Ошибка обновления: {str(e)}')

    try:
        table = client.get(f'/tables/{assignment_id}/')
        employees = client.get('/employees/')
        return render(request, 'tables/update.html', {
            'table': table,
            'employees': employees,
        })
    except Exception as e:
        messages.error(request, f'Ошибка: {str(e)}')
        return redirect('table_list')


@require_session_roles(ROLE_ADMIN, ROLE_MANAGER)
def table_delete(request, assignment_id):
    """Удаление назначения столика."""
    try:
        client = APIClient(request)
        client.delete(f'/tables/{assignment_id}/')
        messages.success(request, 'Назначение столика удалено!')
    except Exception as e:
        messages.error(request, f'Ошибка удаления: {str(e)}')

    return redirect('table_list')
