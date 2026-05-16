"""
Views для управления ролями.
"""
from django.shortcuts import render, redirect
from django.contrib import messages
from core.api_client import APIClient
from core.permissions import ROLE_ADMIN, require_session_roles


@require_session_roles(ROLE_ADMIN)
def role_list(request):
    """Список всех ролей."""
    client = APIClient(request)
    try:
        roles = client.get('/roles/')
    except Exception as e:
        messages.error(request, f'Ошибка загрузки: {str(e)}')
        roles = []
    
    return render(request, 'roles/list.html', {'roles': roles})


@require_session_roles(ROLE_ADMIN)
def role_detail(request, role_id):
    """Детальная информация о роли."""
    client = APIClient(request)
    try:
        role = client.get(f'/roles/{role_id}/')
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
            'description': request.POST.get('description')
        }
        
        try:
            client = APIClient(request)
            client.post('/roles/', data)
            messages.success(request, 'Роль успешно создана!')
            return redirect('role_list')
        except Exception as e:
            messages.error(request, f'Ошибка создания: {str(e)}')
    
    return render(request, 'roles/create.html')


@require_session_roles(ROLE_ADMIN)
def role_update(request, role_id):
    """Обновление роли."""
    client = APIClient(request)
    
    if request.method == 'POST':
        data = {
            'name': request.POST.get('name'),
            'description': request.POST.get('description')
        }
        
        try:
            client.put(f'/roles/{role_id}/', data)
            messages.success(request, 'Роль обновлена!')
            return redirect('role_list')
        except Exception as e:
            messages.error(request, f'Ошибка обновления: {str(e)}')
    
    try:
        role = client.get(f'/roles/{role_id}/')
        return render(request, 'roles/update.html', {'role': role})
    except Exception as e:
        messages.error(request, f'Ошибка: {str(e)}')
        return redirect('role_list')


@require_session_roles(ROLE_ADMIN)
def role_delete(request, role_id):
    """Удаление роли."""
    try:
        client = APIClient(request)
        client.delete(f'/roles/{role_id}/')
        messages.success(request, 'Роль удалена!')
    except Exception as e:
        messages.error(request, f'Ошибка удаления: {str(e)}')
    
    return redirect('role_list')
