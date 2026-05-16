"""
Views для управления меню ресторана.
"""
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from core.api_client import APIClient
from core.api_helpers import menu_dishes_for
from core.permissions import ROLE_ADMIN, ROLE_MANAGER, require_session_roles
import requests


def menu_list(request):
    """Список всех меню."""
    client = APIClient(request)
    try:
        menus = client.get('/menus/')
    except Exception as e:
        messages.error(request, f'Ошибка загрузки: {str(e)}')
        menus = []
    
    return render(request, 'menus/list.html', {'menus': menus})


def menu_detail(request, menu_id):
    """Детальная информация о меню."""
    client = APIClient(request)
    try:
        menu = client.get(f'/menus/{menu_id}/')
        dishes = client.get('/dishes/')
        dishes_dict = {d['id']: d for d in dishes if isinstance(d, dict) and 'id' in d}
        return render(request, 'menus/detail.html', {
            'menu': menu,
            'dishes_dict': dishes_dict,
            'menu_dishes': menu_dishes_for(menu, dishes_dict),
        })
    except Exception as e:
        messages.error(request, f'Ошибка: {str(e)}')
        return redirect('menu_list')


@require_session_roles(ROLE_ADMIN, ROLE_MANAGER)
def menu_create(request):
    """Создание нового меню."""
    client = APIClient(request)
    
    if request.method == 'POST':
        dish_ids = request.POST.getlist('dish_ids')
        data = {
            'name': request.POST.get('name'),
            'dish_ids': [int(i) for i in dish_ids]
        }
        
        try:
            client.post('/menus/', data)
            messages.success(request, 'Меню успешно создано!')
            return redirect('menu_list')
        except Exception as e:
            messages.error(request, f'Ошибка создания: {str(e)}')
    
    try:
        dishes = client.get('/dishes/')
    except:
        dishes = []
    
    return render(request, 'menus/create.html', {'dishes': dishes})


@require_session_roles(ROLE_ADMIN, ROLE_MANAGER)
def menu_update(request, menu_id):
    """Обновление меню."""
    client = APIClient(request)
    
    if request.method == 'POST':
        dish_ids = request.POST.getlist('dish_ids')
        data = {
            'name': request.POST.get('name'),
            'dish_ids': [int(i) for i in dish_ids]
        }
        
        try:
            client.put(f'/menus/{menu_id}/', data)
            messages.success(request, 'Меню обновлено!')
            return redirect('menu_list')
        except Exception as e:
            messages.error(request, f'Ошибка обновления: {str(e)}')
    
    try:
        menu = client.get(f'/menus/{menu_id}/')
        dishes = client.get('/dishes/')
        return render(request, 'menus/update.html', {
            'menu': menu,
            'dishes': dishes
        })
    except Exception as e:
        messages.error(request, f'Ошибка: {str(e)}')
        return redirect('menu_list')


@require_session_roles(ROLE_ADMIN, ROLE_MANAGER)
def menu_delete(request, menu_id):
    """Удаление меню."""
    try:
        client = APIClient(request)
        client.delete(f'/menus/{menu_id}/')
        messages.success(request, 'Меню удалено!')
    except Exception as e:
        messages.error(request, f'Ошибка удаления: {str(e)}')
    
    return redirect('menu_list')


@require_session_roles(ROLE_ADMIN, ROLE_MANAGER)
def menu_export_docx(request, menu_id):
    """Экспорт меню в DOCX."""
    from django.conf import settings
    try:
        token = request.session.get('access_token', '')
        url = f"{settings.API_BASE_URL}/menus/{menu_id}/export/docx"
        resp = requests.get(url, headers={'Authorization': f'Bearer {token}'}, timeout=30)
        resp.raise_for_status()
        response = HttpResponse(
            resp.content,
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        response['Content-Disposition'] = f'attachment; filename=menu_{menu_id}.docx'
        return response
    except Exception as e:
        messages.error(request, f'Ошибка экспорта DOCX: {str(e)}')
        return redirect('menu_detail', menu_id=menu_id)


@require_session_roles(ROLE_ADMIN, ROLE_MANAGER)
def menu_export_xlsx(request, menu_id):
    """Экспорт меню в XLSX."""
    from django.conf import settings
    try:
        token = request.session.get('access_token', '')
        url = f"{settings.API_BASE_URL}/menus/{menu_id}/export/xlsx"
        resp = requests.get(url, headers={'Authorization': f'Bearer {token}'}, timeout=30)
        resp.raise_for_status()
        response = HttpResponse(
            resp.content,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename=menu_{menu_id}.xlsx'
        return response
    except Exception as e:
        messages.error(request, f'Ошибка экспорта XLSX: {str(e)}')
        return redirect('menu_detail', menu_id=menu_id)
