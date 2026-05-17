"""
Views для управления ролями.
"""
from django.shortcuts import render, redirect
from django.contrib import messages
from core.controllers.role_controller import RoleController
from core.permissions import ROLE_ADMIN, require_session_roles


@require_session_roles(ROLE_ADMIN)
def role_list(request):
    """Список ролей с поиском по названию."""
    controller = RoleController(request)
    q = (request.GET.get('q') or '').strip()
    try:
        roles = controller.search(q) if q else controller.list()
    except Exception as e:
        messages.error(request, f'Ошибка загрузки: {str(e)}')
        roles = []

    return render(request, 'roles/list.html', {'roles': roles, 'search_q': q})


@require_session_roles(ROLE_ADMIN)
def role_detail(request, role_id):
    """Детальная информация о роли."""
    try:
        role = RoleController(request).get(role_id)
        return render(request, 'roles/detail.html', {'role': role})
    except Exception as e:
        messages.error(request, f'Ошибка: {str(e)}')
        return redirect('role_list')


@require_session_roles(ROLE_ADMIN)
def role_create(request):
    """Создание новой роли."""
    if request.method == 'POST':
        data = {
            'name': request.POST.get('name'),
            'description': request.POST.get('description'),
        }
        try:
            RoleController(request).create(data)
            messages.success(request, 'Роль успешно создана!')
            return redirect('role_list')
        except Exception as e:
            messages.error(request, f'Ошибка создания: {str(e)}')

    return render(request, 'roles/form.html')


@require_session_roles(ROLE_ADMIN)
def role_update(request, role_id):
    """Обновление роли."""
    controller = RoleController(request)

    if request.method == 'POST':
        data = {
            'name': request.POST.get('name'),
            'description': request.POST.get('description'),
        }
        try:
            controller.update(role_id, data)
            messages.success(request, 'Роль обновлена!')
            return redirect('role_list')
        except Exception as e:
            messages.error(request, f'Ошибка обновления: {str(e)}')

    try:
        role = controller.get(role_id)
        return render(request, 'roles/form.html', {'role': role})
    except Exception as e:
        messages.error(request, f'Ошибка: {str(e)}')
        return redirect('role_list')


@require_session_roles(ROLE_ADMIN)
def role_delete(request, role_id):
    """Удаление роли."""
    try:
        RoleController(request).delete(role_id)
        messages.success(request, 'Роль удалена!')
    except Exception as e:
        messages.error(request, f'Ошибка удаления: {str(e)}')

    return redirect('role_list')
