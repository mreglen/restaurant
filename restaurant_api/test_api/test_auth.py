"""
Тесты для эндпоинтов аутентификации: /api/v1/auth/register и /api/v1/auth/login.

Поскольку auth-роутер НЕ использует get_current_user/require_roles, здесь
мы подставляем только тестовую БД и работаем с реальной логикой AuthService.
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import get_db
from test_api.conftest import override_get_db, TestingSessionLocal
from app.models.role import Role


@pytest.fixture()
def auth_client():
    """Клиент только с переопределённой БД (без фейковой авторизации)."""
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def _ensure_roles():
    """Создаёт базовые роли перед каждым тестом авторизации."""
    db = TestingSessionLocal()
    for rid, name in [(1, "admin"), (2, "manager"), (3, "waiter")]:
        if not db.query(Role).filter(Role.id == rid).first():
            db.add(Role(id=rid, name=name, description=name))
    db.commit()
    db.close()


# ───────────────────────── REGISTER ─────────────────────────
class TestRegister:
    """Тесты эндпоинта POST /api/v1/auth/register."""

    def test_register_success(self, auth_client: TestClient):
        """Успешная регистрация нового пользователя."""
        resp = auth_client.post("/api/v1/auth/register", json={
            "last_name": "Тестов",
            "first_name": "Тест",
            "patronymic": "Тестович",
            "role": 1,
            "phone": "+79001111111",
            "username": "newuser",
            "password": "strongpassword"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_register_duplicate_username(self, auth_client: TestClient):
        """Повторная регистрация с тем же username должна вернуть 400."""
        payload = {
            "last_name": "Тестов",
            "first_name": "Тест",
            "role": 1,
            "username": "dupuser",
            "password": "pass123"
        }
        auth_client.post("/api/v1/auth/register", json=payload)
        resp = auth_client.post("/api/v1/auth/register", json=payload)
        assert resp.status_code == 400

    def test_register_missing_fields(self, auth_client: TestClient):
        """Отсутствие обязательных полей должно вернуть 422."""
        resp = auth_client.post("/api/v1/auth/register", json={
            "username": "noname"
        })
        assert resp.status_code == 422


# ───────────────────────── LOGIN ─────────────────────────
class TestLogin:
    """Тесты эндпоинта POST /api/v1/auth/login."""

    def test_login_success(self, auth_client: TestClient):
        """Успешный логин после регистрации."""
        auth_client.post("/api/v1/auth/register", json={
            "last_name": "Логин",
            "first_name": "Тест",
            "role": 2,
            "username": "loginuser",
            "password": "mypassword"
        })
        resp = auth_client.post(
            "/api/v1/auth/login",
            data={"username": "loginuser", "password": "mypassword"},
        )
        assert resp.status_code == 200
        assert "access_token" in resp.json()

    def test_login_wrong_password(self, auth_client: TestClient):
        """Неверный пароль должен вернуть 401."""
        auth_client.post("/api/v1/auth/register", json={
            "last_name": "Bad",
            "first_name": "Pass",
            "role": 1,
            "username": "badpassuser",
            "password": "correctpass"
        })
        resp = auth_client.post(
            "/api/v1/auth/login",
            data={"username": "badpassuser", "password": "wrongpass"},
        )
        assert resp.status_code in (400, 401)

    def test_login_nonexistent_user(self, auth_client: TestClient):
        """Логин несуществующего пользователя должен вернуть ошибку."""
        resp = auth_client.post(
            "/api/v1/auth/login",
            data={"username": "noone", "password": "nopass"},
        )
        assert resp.status_code in (400, 401)

    def test_login_missing_fields(self, auth_client: TestClient):
        """Отсутствие полей при логине должно вернуть 422."""
        resp = auth_client.post("/api/v1/auth/login", data={})
        assert resp.status_code == 422
