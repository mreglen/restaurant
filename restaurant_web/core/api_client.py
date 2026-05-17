"""
Обратно-совместимый шим — переэкспортирует APIClient из core.controllers.base.
Новый код должен импортировать напрямую из core.controllers.
"""
from core.controllers.base import APIClient

__all__ = ['APIClient']
