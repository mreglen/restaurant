"""
Middleware для обработки аутентификации.
"""
from django.shortcuts import redirect
from django.urls import resolve
from core.auth import is_authenticated, backfill_role_id_if_missing


class AuthMiddleware:
    """
    Middleware для проверки аутентификации пользователей.
    Перенаправляет неавторизованных пользователей на страницу входа.
    """
    
    def __init__(self, get_response):
        """
        Инициализация middleware.
        
        Args:
            get_response: Next middleware или view функция
        """
        self.get_response = get_response
        
        # URL-адреса, не требующие аутентификации
        self.public_urls = [
            'login',
            'register',
            'public_home',
            'public_menu',
            'public_dishes',
        ]
    
    def __call__(self, request):
        """
        Обработка запроса.
        
        Args:
            request: Django request объект
            
        Returns:
            Response объект
        """
        # Получаем имя текущего URL
        match = resolve(request.path_info)
        url_name = match.url_name
        
        # Проверяем, требует ли URL аутентификации
        if url_name not in self.public_urls and not url_name.startswith('auth_'):
            if not is_authenticated(request):
                # Сохраняем запрошенный URL для редиректа после входа
                if request.path_info != '/':
                    request.session['next_url'] = request.path_info
                return redirect('login')
            backfill_role_id_if_missing(request)
        
        response = self.get_response(request)
        return response
