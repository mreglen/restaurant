"""
Controllers package — domain-specific API controllers for Restaurant Web.
"""
from core.controllers.base import APIClient
from core.controllers.auth_controller import AuthController
from core.controllers.client_controller import ClientController
from core.controllers.employee_controller import EmployeeController
from core.controllers.role_controller import RoleController
from core.controllers.dish_controller import DishController
from core.controllers.ingredient_controller import IngredientController
from core.controllers.menu_controller import MenuController
from core.controllers.order_controller import OrderController
from core.controllers.table_controller import TableController

__all__ = [
    'APIClient',
    'AuthController',
    'ClientController',
    'EmployeeController',
    'RoleController',
    'DishController',
    'IngredientController',
    'MenuController',
    'OrderController',
    'TableController',
]
