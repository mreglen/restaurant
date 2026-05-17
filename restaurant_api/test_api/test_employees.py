"""
Тесты для эндпоинтов сотрудников: /api/v1/employees.
"""
import pytest
from fastapi.testclient import TestClient


# ───────────────────────── CRUD ─────────────────────────
class TestEmployeeCRUD:
    """CRUD-тесты для сотрудников."""

    def test_create_employee(self, admin_client: TestClient, seed_role):
        """Создание сотрудника администратором."""
        role = seed_role("waiter", "Официант")
        resp = admin_client.post("/api/v1/employees/", json={
            "last_name": "Сотрудников",
            "first_name": "Тест",
            "patronymic": "Тестович",
            "role_id": role.id,
            "phone": "+79001234567",
            "username": "newemployee",
            "password": "securepass"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["username"] == "newemployee"
        assert data["last_name"] == "Сотрудников"
        assert "id" in data

    def test_create_employee_duplicate_username(self, admin_client: TestClient, seed_role):
        """Повторное создание с тем же username → 400."""
        role = seed_role("admin", "Админ")
        payload = {
            "last_name": "Dup",
            "first_name": "User",
            "role_id": role.id,
            "username": "duplicate_emp",
            "password": "pass"
        }
        admin_client.post("/api/v1/employees/", json=payload)
        resp = admin_client.post("/api/v1/employees/", json=payload)
        assert resp.status_code == 400

    def test_list_employees(self, admin_client: TestClient, seed_employee):
        """Получение списка сотрудников."""
        seed_employee(username="emp_list1", role_name="waiter_list")
        resp = admin_client.get("/api/v1/employees/")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)
        assert len(resp.json()) >= 1

    def test_get_employee_by_id(self, admin_client: TestClient, seed_employee):
        """Получение сотрудника по ID."""
        emp = seed_employee(username="emp_get", role_name="role_get")
        resp = admin_client.get(f"/api/v1/employees/{emp.id}")
        assert resp.status_code == 200
        assert resp.json()["username"] == "emp_get"

    def test_get_employee_not_found(self, admin_client: TestClient):
        """Запрос несуществующего сотрудника → 404."""
        resp = admin_client.get("/api/v1/employees/9999")
        assert resp.status_code == 404

    def test_update_employee(self, admin_client: TestClient, seed_employee):
        """Обновление данных сотрудника."""
        emp = seed_employee(username="emp_upd", role_name="role_upd")
        resp = admin_client.put(f"/api/v1/employees/{emp.id}", json={
            "first_name": "Обновлённый",
            "phone": "+79998887766"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["first_name"] == "Обновлённый"
        assert data["phone"] == "+79998887766"

    def test_update_employee_not_found(self, admin_client: TestClient):
        """Обновление несуществующего сотрудника → 404."""
        resp = admin_client.put("/api/v1/employees/9999", json={"first_name": "X"})
        assert resp.status_code == 404

    def test_delete_employee(self, admin_client: TestClient, seed_employee):
        """Удаление сотрудника."""
        emp = seed_employee(username="emp_del", role_name="role_del")
        resp = admin_client.delete(f"/api/v1/employees/{emp.id}")
        assert resp.status_code == 200

        resp2 = admin_client.get(f"/api/v1/employees/{emp.id}")
        assert resp2.status_code == 404

    def test_delete_employee_not_found(self, admin_client: TestClient):
        """Удаление несуществующего сотрудника → 404."""
        resp = admin_client.delete("/api/v1/employees/9999")
        assert resp.status_code == 404


# ───────────────────────── SEARCH ─────────────────────────
class TestEmployeeSearch:
    """Тесты поиска сотрудников."""

    def test_search_employees(self, admin_client: TestClient, seed_employee):
        """Поиск сотрудника по имени."""
        seed_employee(
            username="emp_search",
            role_name="role_search",
            first_name="Алексей",
            last_name="Поисков",
        )
        resp = admin_client.get("/api/v1/employees/search/", params={"q": "Алексей"})
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

    def test_search_no_results(self, admin_client: TestClient):
        """Поиск без результатов."""
        resp = admin_client.get("/api/v1/employees/search/", params={"q": "zzzznotfound"})
        assert resp.status_code == 200
        assert resp.json() == []


# ───────────────────────── ACCESS ─────────────────────────
class TestEmployeeAccess:
    """Тесты контроля доступа к сотрудникам."""

    def test_manager_can_list_employees(self, manager_client: TestClient, seed_employee):
        """Менеджер может просматривать сотрудников."""
        seed_employee(username="emp_mgr", role_name="role_mgr")
        resp = manager_client.get("/api/v1/employees/")
        assert resp.status_code == 200

    def test_manager_can_update_employee(self, manager_client: TestClient, seed_employee):
        """Менеджер может редактировать карточку сотрудника."""
        emp = seed_employee(username="emp_upd", role_name="waiter_role")
        resp = manager_client.put(f"/api/v1/employees/{emp.id}", json={
            "last_name": "Обновлён",
            "first_name": emp.first_name,
            "patronymic": emp.patronymic or "",
            "role_id": emp.role_id,
            "phone": emp.phone,
        })
        assert resp.status_code == 200
        assert resp.json()["last_name"] == "Обновлён"

    def test_manager_cannot_create_employee(self, manager_client: TestClient, seed_role):
        """Менеджер не может создавать сотрудников → 403."""
        role = seed_role("some_role")
        resp = manager_client.post("/api/v1/employees/", json={
            "last_name": "X",
            "first_name": "Y",
            "role_id": role.id,
            "username": "nope",
            "password": "pass"
        })
        assert resp.status_code == 403

    def test_waiter_cannot_access_employees(self, waiter_client: TestClient):
        """Официант не может просматривать сотрудников → 403."""
        resp = waiter_client.get("/api/v1/employees/")
        assert resp.status_code == 403
