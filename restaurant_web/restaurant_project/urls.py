"""
URL configuration for restaurant_project.
"""
from django.contrib import admin
from django.urls import path
from core.views import (
    login_view, register_view, logout_view,
    dashboard_view,
    admin_panel_view,
    client_list, client_detail, client_create, client_update, client_delete, client_purge,
    employee_list, employee_detail, employee_create, employee_update, employee_delete,
    role_list, role_create, role_detail, role_update, role_delete,
    dish_list, dish_detail, dish_create, dish_update, dish_delete,
    ingredient_list, ingredient_create, ingredient_update, ingredient_delete,
    menu_list, menu_detail, menu_create, menu_update, menu_delete,
    menu_export_docx, menu_export_xlsx,
    order_list, order_detail, order_create, order_update, order_delete, order_statistics,
    table_list, table_create, table_detail, table_update, table_delete,
    public_home, public_menu, public_dishes,
    api_endpoints_catalog_view,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Public pages (no authentication required)
    path('', public_home, name='public_home'),
    path('menu/', public_menu, name='public_menu'),
    path('dishes/', public_dishes, name='public_dishes'),
    
    # Authentication
    path('auth/login/', login_view, name='login'),
    path('auth/register/', register_view, name='register'),
    path('auth/logout/', logout_view, name='logout'),
    
    # Dashboard
    path('dashboard/', dashboard_view, name='dashboard'),

    # Staff admin hub (aggregated lists + links to CRUD)
    path('admin-panel/', admin_panel_view, name='admin_panel'),

    # API catalog (OpenAPI via requests)
    path('api/endpoints/', api_endpoints_catalog_view, name='api_endpoints_catalog'),
    
    # Clients (purge before <int:client_id>)
    path('clients/purge/', client_purge, name='client_purge'),
    path('clients/', client_list, name='client_list'),
    path('clients/create/', client_create, name='client_create'),
    path('clients/<int:client_id>/', client_detail, name='client_detail'),
    path('clients/<int:client_id>/update/', client_update, name='client_update'),
    path('clients/<int:client_id>/delete/', client_delete, name='client_delete'),
    
    # Employees
    path('employees/', employee_list, name='employee_list'),
    path('employees/create/', employee_create, name='employee_create'),
    path('employees/<int:employee_id>/', employee_detail, name='employee_detail'),
    path('employees/<int:employee_id>/update/', employee_update, name='employee_update'),
    path('employees/<int:employee_id>/delete/', employee_delete, name='employee_delete'),
    
    # Roles
    path('roles/', role_list, name='role_list'),
    path('roles/create/', role_create, name='role_create'),
    path('roles/<int:role_id>/', role_detail, name='role_detail'),
    path('roles/<int:role_id>/update/', role_update, name='role_update'),
    path('roles/<int:role_id>/delete/', role_delete, name='role_delete'),
    
    # Dishes
    path('dishes/list/', dish_list, name='dish_list'),
    path('dishes/create/', dish_create, name='dish_create'),
    path('dishes/<int:dish_id>/', dish_detail, name='dish_detail'),
    path('dishes/<int:dish_id>/update/', dish_update, name='dish_update'),
    path('dishes/<int:dish_id>/delete/', dish_delete, name='dish_delete'),
    
    # Ingredients
    path('ingredients/', ingredient_list, name='ingredient_list'),
    path('ingredients/create/', ingredient_create, name='ingredient_create'),
    path('ingredients/<int:ingredient_id>/update/', ingredient_update, name='ingredient_update'),
    path('ingredients/<int:ingredient_id>/delete/', ingredient_delete, name='ingredient_delete'),
    
    # Menus
    path('menus/', menu_list, name='menu_list'),
    path('menus/create/', menu_create, name='menu_create'),
    path('menus/<int:menu_id>/', menu_detail, name='menu_detail'),
    path('menus/<int:menu_id>/update/', menu_update, name='menu_update'),
    path('menus/<int:menu_id>/delete/', menu_delete, name='menu_delete'),
    path('menus/<int:menu_id>/export/docx/', menu_export_docx, name='menu_export_docx'),
    path('menus/<int:menu_id>/export/xlsx/', menu_export_xlsx, name='menu_export_xlsx'),
    
    # Orders (statistics before <int:order_id>)
    path('orders/statistics/', order_statistics, name='order_statistics'),
    path('orders/', order_list, name='order_list'),
    path('orders/create/', order_create, name='order_create'),
    path('orders/<int:order_id>/', order_detail, name='order_detail'),
    path('orders/<int:order_id>/update/', order_update, name='order_update'),
    path('orders/<int:order_id>/delete/', order_delete, name='order_delete'),
    
    # Table assignments
    path('tables/', table_list, name='table_list'),
    path('tables/create/', table_create, name='table_create'),
    path('tables/<int:assignment_id>/', table_detail, name='table_detail'),
    path('tables/<int:assignment_id>/update/', table_update, name='table_update'),
    path('tables/<int:assignment_id>/delete/', table_delete, name='table_delete'),
]
