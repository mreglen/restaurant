"""
Тесты для эндпоинтов клиентов: /api/v1/clients.
"""
import pytest
from fastapi.testclient import TestClient


# ───────────────────────── CRUD ─────────────────────────
class TestClientCRUD:
    """CRUD-тесты для клиентов."""

    def test_create_client(self, admin_client: TestClient):
        """Создание клиента администратором."""
        resp = admin_client.post("/api/v1/clients/", json={
            "last_name": "Иванов",
            "first_name": "Иван",
            "patronymic": "Иванович",
            "phone": "+79001112233",
            "is_vip": False,
            "bonus_points": 0
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["last_name"] == "Иванов"
        assert data["first_name"] == "Иван"
        assert "id" in data

    def test_create_client_minimal(self, admin_client: TestClient):
        """Создание клиента с минимальным набором полей."""
        resp = admin_client.post("/api/v1/clients/", json={
            "last_name": "Тест",
            "first_name": "Мин",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["is_vip"] is False
        assert data["bonus_points"] == 0

    def test_list_clients(self, admin_client: TestClient, seed_client):
        """Получение списка всех клиентов."""
        seed_client("Анна", "Антонова")
        seed_client("Борис", "Борисов")

        resp = admin_client.get("/api/v1/clients/")
        assert resp.status_code == 200
        assert len(resp.json()) >= 2

    def test_get_client_by_id(self, admin_client: TestClient, seed_client):
        """Получение клиента по ID."""
        cl = seed_client("Мария", "Сидорова")
        resp = admin_client.get(f"/api/v1/clients/{cl.id}")
        assert resp.status_code == 200
        assert resp.json()["first_name"] == "Мария"

    def test_get_client_not_found(self, admin_client: TestClient):
        """Запрос несуществующего клиента → 404."""
        resp = admin_client.get("/api/v1/clients/9999")
        assert resp.status_code == 404

    def test_update_client(self, admin_client: TestClient, seed_client):
        """Обновление клиента."""
        cl = seed_client()
        resp = admin_client.put(f"/api/v1/clients/{cl.id}", json={
            "first_name": "Обновлённое",
            "is_vip": True,
            "bonus_points": 100
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["first_name"] == "Обновлённое"
        assert data["is_vip"] is True
        assert data["bonus_points"] == 100

    def test_update_client_partial(self, admin_client: TestClient, seed_client):
        """Частичное обновление клиента (только одно поле)."""
        cl = seed_client()
        resp = admin_client.put(f"/api/v1/clients/{cl.id}", json={
            "phone": "+79999999999"
        })
        assert resp.status_code == 200
        assert resp.json()["phone"] == "+79999999999"

    def test_update_client_not_found(self, admin_client: TestClient):
        """Обновление несуществующего клиента → 404."""
        resp = admin_client.put("/api/v1/clients/9999", json={"first_name": "X"})
        assert resp.status_code == 404

    def test_delete_client(self, admin_client: TestClient, seed_client):
        """Удаление клиента."""
        cl = seed_client()
        resp = admin_client.delete(f"/api/v1/clients/{cl.id}")
        assert resp.status_code == 200

        resp2 = admin_client.get(f"/api/v1/clients/{cl.id}")
        assert resp2.status_code == 404

    def test_delete_client_not_found(self, admin_client: TestClient):
        """Удаление несуществующего клиента → 404."""
        resp = admin_client.delete("/api/v1/clients/9999")
        assert resp.status_code == 404


# ───────────────────────── SEARCH ─────────────────────────
class TestClientSearch:
    """Тесты поиска клиентов."""

    def test_search_clients_by_name(self, admin_client: TestClient, seed_client):
        """Поиск клиента по имени."""
        seed_client("Александр", "Петров")
        seed_client("Елена", "Сидорова")

        resp = admin_client.get("/api/v1/clients/search/", params={"q": "Алекс"})
        assert resp.status_code == 200
        results = resp.json()
        assert len(results) >= 1
        assert any("Александр" in r["first_name"] for r in results)

    def test_search_clients_by_lastname(self, admin_client: TestClient, seed_client):
        """Поиск клиента по фамилии."""
        seed_client("Тест", "Сидоров")
        resp = admin_client.get("/api/v1/clients/search/", params={"q": "Сидоров"})
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

    def test_search_no_results(self, admin_client: TestClient):
        """Поиск без результатов возвращает пустой список."""
        resp = admin_client.get("/api/v1/clients/search/", params={"q": "xyznonexist"})
        assert resp.status_code == 200
        assert resp.json() == []


# ───────────────────────── ACCESS ─────────────────────────
class TestClientAccess:
    """Тесты контроля доступа к клиентам."""

    def test_waiter_cannot_create_client(self, waiter_client: TestClient):
        """Официант не может создавать клиентов → 403."""
        resp = waiter_client.post("/api/v1/clients/", json={
            "last_name": "Нет", "first_name": "Доступа"
        })
        assert resp.status_code == 403

    def test_waiter_can_read_clients(self, waiter_client: TestClient, seed_client):
        """Официант может читать список клиентов."""
        seed_client()
        resp = waiter_client.get("/api/v1/clients/")
        assert resp.status_code == 200

    def test_waiter_cannot_delete_client(self, waiter_client: TestClient, seed_client):
        """Официант не может удалять клиентов → 403."""
        cl = seed_client()
        resp = waiter_client.delete(f"/api/v1/clients/{cl.id}")
        assert resp.status_code == 403

    def test_manager_can_create_client(self, manager_client: TestClient):
        """Менеджер может создавать клиентов."""
        resp = manager_client.post("/api/v1/clients/", json={
            "last_name": "Менеджерский", "first_name": "Клиент"
        })
        assert resp.status_code == 200
