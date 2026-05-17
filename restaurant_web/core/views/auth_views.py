"""
Views для аутентификации пользователей.
"""
from django.shortcuts import render, redirect
from django.contrib import messages
from core.auth import login_user, register_user, logout_user, is_authenticated
from core.permissions import REGISTRATION_ROLE_CHOICES, ROLE_WAITER


def login_view(request):
    """Страница входа в систему."""
    if is_authenticated(request):
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        try:
            login_user(username, password, request)
            messages.success(request, 'Вы успешно вошли в систему!')
            
            # Редирект на запрошенную страницу или на dashboard
            next_url = request.session.pop('next_url', None)
            return redirect(next_url if next_url else 'dashboard')
        except Exception as e:
            messages.error(request, f'Ошибка входа: {str(e)}')
    
    return render(request, 'auth/login.html')


def register_view(request):
    """Страница регистрации нового пользователя."""
    if is_authenticated(request):
        return redirect('dashboard')
    
    if request.method == 'POST':
        last_name = request.POST.get('last_name', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        patronymic = (request.POST.get('patronymic') or '').strip()
        phone = request.POST.get('phone')
        username = request.POST.get('username')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        
        if password != password_confirm:
            messages.error(request, 'Пароли не совпадают!')
            return render(request, 'auth/register.html', {'roles': REGISTRATION_ROLE_CHOICES})

        try:
            register_user(last_name, first_name, patronymic, ROLE_WAITER, phone, username, password, request)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('dashboard')
        except Exception as e:
            messages.error(request, f'Ошибка регистрации: {str(e)}')

    return render(request, 'auth/register.html', {'roles': REGISTRATION_ROLE_CHOICES})


def logout_view(request):
    """Выход из системы."""
    logout_user(request)
    messages.success(request, 'Вы вышли из системы!')
    return redirect('login')
