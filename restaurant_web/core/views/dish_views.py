"""
Views для управления блюдами.
"""
from django.shortcuts import render, redirect
from django.contrib import messages
from core.api_client import APIClient
from core.permissions import ROLE_ADMIN, ROLE_MANAGER, require_session_roles


def dish_list(request):
    """Список всех блюд."""
    client = APIClient(request)
    try:
        dishes = client.get('/dishes/')
        ingredients = client.get('/ingredients/')
        ingredients_dict = {i['id']: i['name'] for i in ingredients}
    except Exception as e:
        messages.error(request, f'Ошибка загрузки: {str(e)}')
        dishes = []
        ingredients_dict = {}

    return render(request, 'dishes/list.html', {
        'dishes': dishes,
        'ingredients_dict': ingredients_dict,
    })


def dish_detail(request, dish_id):
    """Детальная информация о блюде и названия ингредиентов."""
    client = APIClient(request)
    try:
        dish = client.get(f'/dishes/{dish_id}/')
        ingredients = client.get('/ingredients/')
        ing_by_id = {i['id']: i['name'] for i in ingredients}
        raw_ids = dish.get('ingredients') or []
        ingredient_rows = [
            {'id': iid, 'name': ing_by_id.get(iid, f'Ингредиент #{iid}')}
            for iid in raw_ids
        ]
        return render(request, 'dishes/detail.html', {
            'dish': dish,
            'ingredient_rows': ingredient_rows,
        })
    except Exception as e:
        messages.error(request, f'Ошибка: {str(e)}')
        return redirect('dish_list')


@require_session_roles(ROLE_ADMIN, ROLE_MANAGER)
def dish_create(request):
    """Создание нового блюда."""
    client = APIClient(request)

    if request.method == 'POST':
        ingredient_ids = request.POST.getlist('ingredient_ids')
        data = {
            'name': request.POST.get('name'),
            'description': request.POST.get('description'),
            'price': float(request.POST.get('price')),
            'ingredient_ids': [int(i) for i in ingredient_ids],
        }

        try:
            client.post('/dishes/', data)
            messages.success(request, 'Блюдо успешно создано!')
            return redirect('dish_list')
        except Exception as e:
            messages.error(request, f'Ошибка создания: {str(e)}')

    try:
        ingredients = client.get('/ingredients/')
    except Exception:
        ingredients = []

    return render(request, 'dishes/create.html', {'ingredients': ingredients})


@require_session_roles(ROLE_ADMIN, ROLE_MANAGER)
def dish_update(request, dish_id):
    """Обновление данных блюда."""
    client = APIClient(request)

    if request.method == 'POST':
        ingredient_ids = request.POST.getlist('ingredient_ids')
        data = {
            'name': request.POST.get('name'),
            'description': request.POST.get('description'),
            'price': float(request.POST.get('price')),
            'ingredient_ids': [int(i) for i in ingredient_ids],
        }

        try:
            client.put(f'/dishes/{dish_id}/', data)
            messages.success(request, 'Блюдо обновлено!')
            return redirect('dish_list')
        except Exception as e:
            messages.error(request, f'Ошибка обновления: {str(e)}')

    try:
        dish = client.get(f'/dishes/{dish_id}/')
        ingredients = client.get('/ingredients/')
        return render(request, 'dishes/update.html', {
            'dish': dish,
            'ingredients': ingredients,
        })
    except Exception as e:
        messages.error(request, f'Ошибка: {str(e)}')
        return redirect('dish_list')


@require_session_roles(ROLE_ADMIN, ROLE_MANAGER)
def dish_delete(request, dish_id):
    """Удаление блюда."""
    try:
        client = APIClient(request)
        client.delete(f'/dishes/{dish_id}/')
        messages.success(request, 'Блюдо удалено!')
    except Exception as e:
        messages.error(request, f'Ошибка удаления: {str(e)}')

    return redirect('dish_list')
