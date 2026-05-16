"""
Views для управления ингредиентами.
"""
from django.shortcuts import render, redirect
from django.contrib import messages
from core.api_client import APIClient
from core.permissions import ROLE_ADMIN, ROLE_MANAGER, require_session_roles


def ingredient_list(request):
    """Список всех ингредиентов."""
    client = APIClient(request)
    try:
        ingredients = client.get('/ingredients/')
    except Exception as e:
        messages.error(request, f'Ошибка загрузки: {str(e)}')
        ingredients = []
    
    return render(request, 'ingredients/list.html', {'ingredients': ingredients})


@require_session_roles(ROLE_ADMIN, ROLE_MANAGER)
def ingredient_create(request):
    """Создание нового ингредиента."""
    if request.method == 'POST':
        data = {
            'name': request.POST.get('name')
        }
        
        try:
            client = APIClient(request)
            client.post('/ingredients/', data)
            messages.success(request, 'Ингредиент успешно создан!')
            return redirect('ingredient_list')
        except Exception as e:
            messages.error(request, f'Ошибка создания: {str(e)}')
    
    return render(request, 'ingredients/create.html')


@require_session_roles(ROLE_ADMIN, ROLE_MANAGER)
def ingredient_update(request, ingredient_id):
    """Обновление ингредиента."""
    client = APIClient(request)
    
    if request.method == 'POST':
        data = {
            'name': request.POST.get('name')
        }
        
        try:
            client.put(f'/ingredients/{ingredient_id}/', data)
            messages.success(request, 'Ингредиент обновлен!')
            return redirect('ingredient_list')
        except Exception as e:
            messages.error(request, f'Ошибка обновления: {str(e)}')
    
    try:
        ingredient = client.get(f'/ingredients/{ingredient_id}/')
        return render(request, 'ingredients/update.html', {'ingredient': ingredient})
    except Exception as e:
        messages.error(request, f'Ошибка: {str(e)}')
        return redirect('ingredient_list')


@require_session_roles(ROLE_ADMIN, ROLE_MANAGER)
def ingredient_delete(request, ingredient_id):
    """Удаление ингредиента."""
    try:
        client = APIClient(request)
        client.delete(f'/ingredients/{ingredient_id}/')
        messages.success(request, 'Ингредиент удален!')
    except Exception as e:
        messages.error(request, f'Ошибка удаления: {str(e)}')
    
    return redirect('ingredient_list')
