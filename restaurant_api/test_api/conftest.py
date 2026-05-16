"""
Общие фикстуры для тестов API.

Используется отдельная БД TEST_DATABASE_URL (по умолчанию restaurant_test).
Перед каждым тестом таблицы очищаются для изоляции.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import settings
from app.core.database import Base, get_db
from app.db_utils import ensure_postgres_database, resolve_test_database_url
from app.dependencies.auth_deps import get_current_user, require_roles
from app.models.role import Role
from app.models.employee import Employee
from app.models.client import Client
from app.models.ingredient import Ingredient
from app.models.dish import Dish
from app.models.dish_ingredient import DishIngredient
from app.models.menu import Menu
from app.models.menu_item import MenuItem
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.table_assignment import TableAssignment
from app.core.security import hash_password
from app.main import app

# ---------------------------------------------------------------------------
# БД для тестов (отдельная от production/dev)
# ---------------------------------------------------------------------------
SQLALCHEMY_TEST_URL = resolve_test_database_url(
    settings.DATABASE_URL,
    settings.TEST_DATABASE_URL,
)
ensure_postgres_database(SQLALCHEMY_TEST_URL)

engine_test = create_engine(SQLALCHEMY_TEST_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)


def override_get_db():
    """Переопределение зависимости get_db для использования тестовой БД."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Фейковые пользователи
# ---------------------------------------------------------------------------
class FakeUser:
    """Фейковый объект пользователя для переопределения зависимостей авторизации."""

    def __init__(self, user_id: int, role_id: int, username: str = "testuser"):
        self.id = user_id
        self.role_id = role_id
        self.username = username


def make_fake_current_user(role_id: int):
    """Создаёт функцию-зависимость, возвращающую фейкового пользователя с нужной ролью."""
    def _fake():
        return FakeUser(user_id=1, role_id=role_id)
    return _fake


def make_fake_require_roles(role_id: int):
    """Создаёт фабрику зависимостей, имитирующую require_roles для заданной роли."""
    def _factory(allowed_role_ids: list[int]):
        def _checker():
            user = FakeUser(user_id=1, role_id=role_id)
            if user.role_id not in allowed_role_ids:
                from fastapi import HTTPException
                raise HTTPException(status_code=403, detail="Доступ запрещён")
            return user
        return _checker
    return _factory


# ---------------------------------------------------------------------------
# Фикстуры
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Создаёт таблицы в тестовой БД перед первым тестом и удаляет после всех тестов."""
    Base.metadata.create_all(bind=engine_test)
    yield
    Base.metadata.drop_all(bind=engine_test)


@pytest.fixture(autouse=True)
def clean_tables():
    """Очищает все таблицы перед каждым тестом для изоляции."""
    yield
    db = TestingSessionLocal()
    try:
        for table in reversed(Base.metadata.sorted_tables):
            db.execute(table.delete())
        db.commit()
    finally:
        db.close()


@pytest.fixture()
def db_session() -> Session:
    """Возвращает сессию тестовой БД."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def admin_client() -> TestClient:
    """TestClient с правами администратора (role_id=1)."""
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = make_fake_current_user(1)
    app.dependency_overrides[require_roles] = make_fake_require_roles(1)
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture()
def manager_client() -> TestClient:
    """TestClient с правами менеджера (role_id=2)."""
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = make_fake_current_user(2)
    app.dependency_overrides[require_roles] = make_fake_require_roles(2)
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture()
def waiter_client() -> TestClient:
    """TestClient с правами официанта (role_id=3) — ограниченные права."""
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = make_fake_current_user(3)
    app.dependency_overrides[require_roles] = make_fake_require_roles(3)
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture()
def unauth_client() -> TestClient:
    """TestClient без авторизации — только get_db переопределён."""
    app.dependency_overrides[get_db] = override_get_db
    # НЕ переопределяем get_current_user — будет требовать Bearer-токен
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Хелперы для создания тестовых данных
# ---------------------------------------------------------------------------
@pytest.fixture()
def seed_role(db_session: Session):
    """Создаёт тестовую роль и возвращает её."""
    def _create(name: str = "admin", description: str = "Administrator role") -> Role:
        role = Role(name=name, description=description)
        db_session.add(role)
        db_session.commit()
        db_session.refresh(role)
        return role
    return _create


@pytest.fixture()
def seed_employee(db_session: Session, seed_role):
    """Создаёт тестового сотрудника (роль создаётся автоматически)."""
    def _create(
        username: str = "employee1",
        password: str = "password123",
        role_name: str = "waiter",
        role_id: int | None = None,
        first_name: str = "Иван",
        last_name: str = "Иванов",
    ) -> Employee:
        if role_id is None:
            role = seed_role(name=role_name, description=f"Role {role_name}")
            role_id = role.id
        emp = Employee(
            first_name=first_name,
            last_name=last_name,
            patronymic="",
            username=username,
            password_hash=hash_password(password),
            role_id=role_id,
            phone="+79001234567",
        )
        db_session.add(emp)
        db_session.commit()
        db_session.refresh(emp)
        return emp
    return _create


@pytest.fixture()
def seed_client(db_session: Session):
    """Создаёт тестового клиента."""
    def _create(
        first_name: str = "Пётр",
        last_name: str = "Петров",
        phone: str = "+79009876543",
        is_vip: bool = False,
    ) -> Client:
        cl = Client(
            first_name=first_name,
            last_name=last_name,
            patronymic="Петрович",
            phone=phone,
            is_vip=is_vip,
            bonus_points=0,
        )
        db_session.add(cl)
        db_session.commit()
        db_session.refresh(cl)
        return cl
    return _create


@pytest.fixture()
def seed_ingredient(db_session: Session):
    """Создаёт тестовый ингредиент."""
    def _create(name: str = "Помидор") -> Ingredient:
        ing = Ingredient(name=name)
        db_session.add(ing)
        db_session.commit()
        db_session.refresh(ing)
        return ing
    return _create


@pytest.fixture()
def seed_dish(db_session: Session):
    """Создаёт тестовое блюдо."""
    def _create(
        name: str = "Борщ",
        price: float = 350.0,
        description: str = "Традиционный суп",
    ) -> Dish:
        dish = Dish(name=name, description=description, price=price)
        db_session.add(dish)
        db_session.commit()
        db_session.refresh(dish)
        return dish
    return _create
