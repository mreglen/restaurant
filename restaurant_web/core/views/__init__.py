"""
Views module for core app.
"""
from core.views.auth_views import login_view, register_view, logout_view
from core.views.dashboard_view import dashboard_view
from core.views.admin_panel_view import admin_panel_view
from core.views.client_views import client_list, client_detail, client_create, client_update, client_delete, client_purge
from core.views.employee_views import employee_list, employee_detail, employee_create, employee_update, employee_delete
from core.views.role_views import role_list, role_create, role_detail, role_update, role_delete
from core.views.dish_views import dish_list, dish_detail, dish_create, dish_update, dish_delete
from core.views.ingredient_views import ingredient_list, ingredient_create, ingredient_update, ingredient_delete
from core.views.menu_views import menu_list, menu_detail, menu_create, menu_update, menu_delete, menu_export_docx, menu_export_xlsx
from core.views.order_views import order_list, order_detail, order_create, order_update, order_delete, order_statistics
from core.views.table_views import table_list, table_create, table_detail, table_update, table_delete
from core.views.public_views import public_home, public_menu, public_dishes
from core.views.api_catalog_view import api_endpoints_catalog_view

__all__ = [
    'login_view', 'register_view', 'logout_view',
    'dashboard_view',
    'admin_panel_view',
    'client_list', 'client_detail', 'client_create', 'client_update', 'client_delete', 'client_purge',
    'employee_list', 'employee_detail', 'employee_create', 'employee_update', 'employee_delete',
    'role_list', 'role_create', 'role_detail', 'role_update', 'role_delete',
    'dish_list', 'dish_detail', 'dish_create', 'dish_update', 'dish_delete',
    'ingredient_list', 'ingredient_create', 'ingredient_update', 'ingredient_delete',
    'menu_list', 'menu_detail', 'menu_create', 'menu_update', 'menu_delete',
    'menu_export_docx', 'menu_export_xlsx',
    'order_list', 'order_detail', 'order_create', 'order_update', 'order_delete', 'order_statistics',
    'table_list', 'table_create', 'table_detail', 'table_update', 'table_delete',
    'public_home', 'public_menu', 'public_dishes',
    'api_endpoints_catalog_view',
]
