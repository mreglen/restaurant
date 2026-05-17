"""
Views для управления блюдами.
"""
from django.shortcuts import render, redirect
from django.contrib import messages
from core.controllers.dish_controller import DishController
from core.controllers.ingredient_controller import IngredientController
from core.permissions import ROLE_ADMIN, ROLE_MANAGER, require_session_roles


def dish_list(request):
    """Список блюд с поиском по названию."""
    dish_ctrl = DishController(request)
    ing_ctrl = IngredientController(request)
    q = (request.GET.get('q') or '').strip()
    try:
        dishes = dish_ctrl.search(q) if q else dish_ctrl.list()
        ingredients = ing_ctrl.list()
        ingredients_dict = {i['id']: i['name'] for i in ingredients}
    except Exception as e:
        messages.error(request, f'Ошибка загрузки: {str(e)}')
        dishes = []
        ingredients_dict = {}

    return render(request, 'dishes/list.html', {
        'dishes': dishes,
        'ingredients_dict': ingredients_dict,
        'search_q': q,
    })


def dish_detail(request, dish_id):
    """Детальная информация о блюде и названия ингредиентов."""
    dish_ctrl = DishController(request)
    ing_ctrl = IngredientController(request)
    try:
        dish = dish_ctrl.get(dish_id)
        ingredients = ing_ctrl.list()
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
    dish_ctrl = DishController(request)
    ing_ctrl = IngredientController(request)

    if request.method == 'POST':
        ingredient_ids = request.POST.getlist('ingredient_ids')
        data = {
            'name': request.POST.get('name'),
            'description': request.POST.get('description'),
            'price': float(request.POST.get('price')),
            'ingredient_ids': [int(i) for i in ingredient_ids],
        }
        try:
            dish_ctrl.create(data)
            messages.success(request, 'Блюдо успешно создано!')
            return redirect('dish_list')
        except Exception as e:
            messages.error(request, f'Ошибка создания: {str(e)}')

    try:
        ingredients = ing_ctrl.list()
    except Exception:
        ingredients = []

    return render(request, 'dishes/create.html', {'ingredients': ingredients})


@require_session_roles(ROLE_ADMIN, ROLE_MANAGER)
def dish_update(request, dish_id):
    """Обновление данных блюда."""
    dish_ctrl = DishController(request)
    ing_ctrl = IngredientController(request)

    if request.method == 'POST':
        ingredient_ids = request.POST.getlist('ingredient_ids')
        data = {
            'name': request.POST.get('name'),
            'description': request.POST.get('description'),
            'price': float(request.POST.get('price')),
            'ingredient_ids': [int(i) for i in ingredient_ids],
        }
        try:
            dish_ctrl.update(dish_id, data)
            messages.success(request, 'Блюдо обновлено!')
            return redirect('dish_list')
        except Exception as e:
            messages.error(request, f'Ошибка обновления: {str(e)}')

    try:
        dish = dish_ctrl.get(dish_id)
        ingredients = ing_ctrl.list()
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
        DishController(request).delete(dish_id)
        messages.success(request, 'Блюдо удалено!')
    except Exception as e:
        messages.error(request, f'Ошибка удаления: {str(e)}')

    return redirect('dish_list')
