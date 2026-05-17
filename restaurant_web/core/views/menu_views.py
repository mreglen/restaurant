"""
Views для управления меню ресторана.
"""
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from core.controllers.menu_controller import MenuController
from core.controllers.dish_controller import DishController
from core.api_helpers import menu_dishes_for
from core.permissions import ROLE_ADMIN, ROLE_MANAGER, ROLE_WAITER, require_session_roles


def menu_list(request):
    """Список меню с поиском по названию."""
    controller = MenuController(request)
    q = (request.GET.get('q') or '').strip()
    try:
        menus = controller.search(q) if q else controller.list()
    except Exception as e:
        messages.error(request, f'Ошибка загрузки: {str(e)}')
        menus = []

    return render(request, 'menus/list.html', {'menus': menus, 'search_q': q})


def menu_detail(request, menu_id):
    """Детальная информация о меню."""
    menu_ctrl = MenuController(request)
    dish_ctrl = DishController(request)
    try:
        menu = menu_ctrl.get(menu_id)
        dishes = dish_ctrl.list()
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
    menu_ctrl = MenuController(request)
    dish_ctrl = DishController(request)

    if request.method == 'POST':
        dish_ids = request.POST.getlist('dish_ids')
        data = {
            'name': request.POST.get('name'),
            'dish_ids': [int(i) for i in dish_ids],
        }
        try:
            menu_ctrl.create(data)
            messages.success(request, 'Меню успешно создано!')
            return redirect('menu_list')
        except Exception as e:
            messages.error(request, f'Ошибка создания: {str(e)}')

    try:
        dishes = dish_ctrl.list()
    except Exception:
        dishes = []

    return render(request, 'menus/create.html', {'dishes': dishes})


@require_session_roles(ROLE_ADMIN, ROLE_MANAGER)
def menu_update(request, menu_id):
    """Обновление меню."""
    menu_ctrl = MenuController(request)
    dish_ctrl = DishController(request)

    if request.method == 'POST':
        dish_ids = request.POST.getlist('dish_ids')
        data = {
            'name': request.POST.get('name'),
            'dish_ids': [int(i) for i in dish_ids],
        }
        try:
            menu_ctrl.update(menu_id, data)
            messages.success(request, 'Меню обновлено!')
            return redirect('menu_list')
        except Exception as e:
            messages.error(request, f'Ошибка обновления: {str(e)}')

    try:
        menu = menu_ctrl.get(menu_id)
        dishes = dish_ctrl.list()
        return render(request, 'menus/update.html', {
            'menu': menu,
            'dishes': dishes,
        })
    except Exception as e:
        messages.error(request, f'Ошибка: {str(e)}')
        return redirect('menu_list')


@require_session_roles(ROLE_ADMIN, ROLE_MANAGER)
def menu_delete(request, menu_id):
    """Удаление меню."""
    try:
        MenuController(request).delete(menu_id)
        messages.success(request, 'Меню удалено!')
    except Exception as e:
        messages.error(request, f'Ошибка удаления: {str(e)}')

    return redirect('menu_list')


@require_session_roles(ROLE_ADMIN, ROLE_MANAGER, ROLE_WAITER)
def menu_export_docx(request, menu_id):
    """Экспорт меню в DOCX."""
    try:
        resp = MenuController(request).export_docx(menu_id)
        resp.raise_for_status()
        response = HttpResponse(
            resp.content,
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        )
        response['Content-Disposition'] = f'attachment; filename=menu_{menu_id}.docx'
        return response
    except Exception as e:
        messages.error(request, f'Ошибка экспорта DOCX: {str(e)}')
        return redirect('menu_detail', menu_id=menu_id)


@require_session_roles(ROLE_ADMIN, ROLE_MANAGER, ROLE_WAITER)
def menu_export_xlsx(request, menu_id):
    """Экспорт меню в XLSX."""
    try:
        resp = MenuController(request).export_xlsx(menu_id)
        resp.raise_for_status()
        response = HttpResponse(
            resp.content,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        response['Content-Disposition'] = f'attachment; filename=menu_{menu_id}.xlsx'
        return response
    except Exception as e:
        messages.error(request, f'Ошибка экспорта XLSX: {str(e)}')
        return redirect('menu_detail', menu_id=menu_id)
