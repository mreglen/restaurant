"""
Тесты для эндпоинтов ролей: /api/v1/roles.
"""
import pytest
from fastapi.testclient import TestClient


# ───────────────────────── CRUD ─────────────────────────
class TestRoleCRUD:
    """CRUD-тесты для ролей (admin-only)."""

    def test_create_role(self, admin_client: TestClient):
        """Создание роли администратором."""
        resp = admin_client.post("/api/v1/roles/", json={
            "name": "chef",
            "description": "Шеф-повар"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "chef"
        assert data["description"] == "Шеф-повар"
        assert "id" in data

    def test_list_roles(self, admin_client: TestClient, seed_role):
        """Получение списка всех ролей."""
        seed_role("admin", "Администратор")
        seed_role("manager", "Менеджер")

        resp = admin_client.get("/api/v1/roles/")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) >= 2

    def test_get_role_by_id(self, admin_client: TestClient, seed_role):
        """Получение роли по ID."""
        role = seed_role("viewer", "Только чтение")
        resp = admin_client.get(f"/api/v1/roles/{role.id}")
        assert resp.status_code == 200
        assert resp.json()["name"] == "viewer"

    def test_get_role_not_found(self, admin_client: TestClient):
        """Запрос несуществующей роли → 404."""
        resp = admin_client.get("/api/v1/roles/9999")
        assert resp.status_code == 404

    def test_update_role(self, admin_client: TestClient, seed_role):
        """Обновление роли."""
        role = seed_role("old_name", "old desc")
        resp = admin_client.put(f"/api/v1/roles/{role.id}", json={
            "name": "new_name",
            "description": "new desc"
        })
        assert resp.status_code == 200
        assert resp.json()["name"] == "new_name"

    def test_update_role_not_found(self, admin_client: TestClient):
        """Обновление несуществующей роли → 404."""
        resp = admin_client.put("/api/v1/roles/9999", json={
            "name": "x", "description": "y"
        })
        assert resp.status_code == 404

    def test_delete_role(self, admin_client: TestClient, seed_role):
        """Удаление роли."""
        role = seed_role("to_delete", "Будет удалена")
        resp = admin_client.delete(f"/api/v1/roles/{role.id}")
        assert resp.status_code == 200

        resp2 = admin_client.get(f"/api/v1/roles/{role.id}")
        assert resp2.status_code == 404

    def test_delete_role_not_found(self, admin_client: TestClient):
        """Удаление несуществующей роли → 404."""
        resp = admin_client.delete("/api/v1/roles/9999")
        assert resp.status_code == 404


# ───────────────────────── SEARCH ─────────────────────────
class TestRoleSearch:
    """Тесты поиска ролей."""

    def test_search_roles(self, admin_client: TestClient, seed_role):
        """Поиск ролей по подстроке."""
        seed_role("superadmin", "Супер-администратор")
        seed_role("manager", "Менеджер")

        resp = admin_client.get("/api/v1/roles/search/", params={"q": "admin"})
        assert resp.status_code == 200
        names = [r["name"] for r in resp.json()]
        assert any("admin" in n for n in names)

    def test_search_no_results(self, admin_client: TestClient):
        """Поиск без результатов возвращает пустой список."""
        resp = admin_client.get("/api/v1/roles/search/", params={"q": "xyznonexistent"})
        assert resp.status_code == 200
        assert resp.json() == []


# ───────────────────────── ACCESS ─────────────────────────
class TestRoleAccess:
    """Тесты контроля доступа к ролям."""

    def test_waiter_cannot_create_role(self, waiter_client: TestClient):
        """Официант не может создавать роли → 403."""
        resp = waiter_client.post("/api/v1/roles/", json={
            "name": "hacker", "description": "no"
        })
        assert resp.status_code == 403

    def test_manager_cannot_delete_role(self, manager_client: TestClient, seed_role):
        """Менеджер не может удалять роли → 403."""
        role = seed_role("temp")
        resp = manager_client.delete(f"/api/v1/roles/{role.id}")
        assert resp.status_code == 403
