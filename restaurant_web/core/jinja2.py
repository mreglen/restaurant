"""
Настройка Jinja2 environment для Django.
"""
from jinja2 import Environment
from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import reverse
from django.utils import timezone
import jinja2


def format_date(value, format='%d.%m.%Y %H:%M'):
    """Форматирование даты."""
    if value:
        try:
            if isinstance(value, str):
                from datetime import datetime
                value = datetime.fromisoformat(value.replace('Z', '+00:00'))
            return value.strftime(format)
        except:
            return str(value)
    return ''


def format_price(value):
    """Форматирование цены."""
    if value:
        try:
            return f"{float(value):.2f} ₽"
        except:
            return str(value)
    return '0.00 ₽'


def truncate(value, length=50):
    """Обрезка текста."""
    if value and len(str(value)) > length:
        return str(value)[:length] + '...'
    return value


def person_fio(value):
    """ФИО из dict API: full_name или last_name + first_name + patronymic."""
    if not value or not isinstance(value, dict):
        return ''
    if value.get('full_name'):
        return value['full_name']
    parts = [value.get('last_name'), value.get('first_name'), value.get('patronymic') or '']
    return ' '.join(p for p in parts if p).strip()


def django_url(viewname, *args, **kwargs):
    """Обертка над reverse для Jinja2, поддерживающая kwargs напрямую."""
    return reverse(viewname, args=args, kwargs=kwargs)


def environment(**options):
    """
    Создание и настройка Jinja2 environment.
    
    Args:
        options: Опции environment
        
    Returns:
        Environment: Настроенный Jinja2 environment
    """
    env = Environment(**options)
    
    # Глобальные функции
    env.globals.update({
        'static': staticfiles_storage.url,
        'url': django_url,
        'now': timezone.now,
    })
    
    # Фильтры
    env.filters.update({
        'format_date': format_date,
        'format_price': format_price,
        'truncate': truncate,
        'person_fio': person_fio,
    })
    
    return env
