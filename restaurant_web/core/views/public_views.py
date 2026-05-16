"""
Публичные views — доступны без авторизации.
"""
from django.contrib import messages
from django.shortcuts import render

from core.api_helpers import (
    anonymous_api_client,
    fetch_list,
    menu_dishes_for,
    menu_dish_ids,
)


def public_home(request):
    """Публичная главная страница ресторана."""
    client = anonymous_api_client()
    errors: list[str] = []

    dishes, err = fetch_list(client, '/dishes/')
    if err:
        errors.append(err)
    menus, err = fetch_list(client, '/menus/')
    if err:
        errors.append(err)

    for error in errors:
        messages.warning(request, f'Не удалось загрузить данные меню: {error}')

    featured = dishes[:6] if dishes else []
    menu_previews = menus[:3] if menus else []
    dishes_dict = {d['id']: d for d in dishes if isinstance(d, dict) and 'id' in d}

    return render(request, 'index.html', {
        'dishes': featured,
        'menus': menu_previews,
        'dishes_dict': dishes_dict,
        'dishes_count': len(dishes),
        'menus_count': len(menus),
        'api_available': not errors,
    })


def public_menu(request):
    """Публичная страница с меню ресторана."""
    client = anonymous_api_client()
    errors: list[str] = []

    menus, err = fetch_list(client, '/menus/')
    if err:
        errors.append(err)
    dishes, err = fetch_list(client, '/dishes/')
    if err:
        errors.append(err)

    for error in errors:
        messages.warning(request, f'Ошибка загрузки: {error}')

    dishes_dict = {
        d['id']: d for d in dishes if isinstance(d, dict) and 'id' in d
    }
    menus_with_dishes = [
        {
            'id': m['id'],
            'name': m.get('name', 'Меню'),
            'dish_ids': menu_dish_ids(m),
            'dishes': menu_dishes_for(m, dishes_dict),
        }
        for m in menus
        if isinstance(m, dict) and 'id' in m
    ]

    return render(request, 'public/menu.html', {
        'menus': menus_with_dishes,
        'dishes': dishes,
        'dishes_dict': dishes_dict,
        'api_available': not errors,
    })


def public_dishes(request):
    """Публичная страница со списком всех блюд."""
    client = anonymous_api_client()
    dishes, err = fetch_list(client, '/dishes/')
    if err:
        messages.warning(request, f'Ошибка загрузки блюд: {err}')

    return render(request, 'public/dishes.html', {
        'dishes': dishes,
        'api_available': err is None,
    })
