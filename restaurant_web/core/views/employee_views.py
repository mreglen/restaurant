"""
Views для управления сотрудниками.
"""
from django.shortcuts import render, redirect
from django.contrib import messages
from core.controllers.employee_controller import EmployeeController
from core.controllers.role_controller import RoleController
from core.permissions import (
    ROLE_ADMIN,
    ROLE_MANAGER,
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

    emp_ctrl = EmployeeController(request)
    q = (request.GET.get('q') or '').strip()
    try:
        employees = emp_ctrl.search(q) if q else emp_ctrl.list()
        if rid == ROLE_ADMIN:
            roles = RoleController(request).list()
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

    try:
        employee = EmployeeController(request).get(employee_id)
        return render(request, 'employees/detail.html', {'employee': employee})
    except Exception as e:
        messages.error(request, f'Ошибка: {str(e)}')
        return redirect('employee_list')


@require_session_roles(ROLE_ADMIN)
def employee_create(request):
    """Создание нового сотрудника."""
    emp_ctrl = EmployeeController(request)

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
            emp_ctrl.create(data)
            messages.success(request, 'Сотрудник успешно создан!')
            return redirect('employee_list')
        except Exception as e:
            messages.error(request, f'Ошибка создания: {str(e)}')

    try:
        roles = RoleController(request).list()
    except Exception:
        roles = []

    return render(request, 'employees/form.html', {'roles': roles})


@require_session_roles(ROLE_ADMIN, ROLE_MANAGER)
def employee_update(request, employee_id):
    """Обновление данных сотрудника."""
    emp_ctrl = EmployeeController(request)
    rid = role_id_from_session(request.session)

    if request.method == 'POST':
        data = {
            'last_name': request.POST.get('last_name', '').strip(),
            'first_name': request.POST.get('first_name', '').strip(),
            'patronymic': (request.POST.get('patronymic') or '').strip(),
            'role_id': int(request.POST.get('role_id')),
            'phone': request.POST.get('phone'),
        }
        try:
            emp_ctrl.update(employee_id, data)
            messages.success(request, 'Данные сотрудника обновлены!')
            return redirect('employee_list')
        except Exception as e:
            messages.error(request, f'Ошибка обновления: {str(e)}')

    try:
        employee = emp_ctrl.get(employee_id)
        roles = RoleController(request).list() if rid == ROLE_ADMIN else list(REGISTRATION_ROLE_CHOICES)
        return render(request, 'employees/form.html', {
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
        EmployeeController(request).delete(employee_id)
        messages.success(request, 'Сотрудник удален!')
    except Exception as e:
        messages.error(request, f'Ошибка удаления: {str(e)}')

    return redirect('employee_list')
