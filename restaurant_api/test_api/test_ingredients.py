"""
Тесты для эндпоинтов ингредиентов: /api/v1/ingredients.
"""
import pytest
from fastapi.testclient import TestClient


# ───────────────────────── CRUD ─────────────────────────
class TestIngredientCRUD:
    """CRUD-тесты для ингредиентов."""

    def test_create_ingredient(self, admin_client: TestClient):
        """Создание ингредиента."""
        resp = admin_client.post("/api/v1/ingredients/", json={"name": "Мука"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "Мука"
        assert "id" in data

    def test_list_ingredients(self, admin_client: TestClient, seed_ingredient):
        """Получение списка всех ингредиентов."""
        seed_ingredient("Соль")
        seed_ingredient("Перец")

        resp = admin_client.get("/api/v1/ingredients/")
        assert resp.status_code == 200
        assert len(resp.json()) >= 2

    def test_get_ingredient_by_id(self, admin_client: TestClient, seed_ingredient):
        """Получение ингредиента по ID."""
        ing = seed_ingredient("Чеснок")
        resp = admin_client.get(f"/api/v1/ingredients/{ing.id}")
        assert resp.status_code == 200
        assert resp.json()["name"] == "Чеснок"

    def test_get_ingredient_not_found(self, admin_client: TestClient):
        """Запрос несуществующего ингредиента → 404."""
        resp = admin_client.get("/api/v1/ingredients/9999")
        assert resp.status_code == 404

    def test_update_ingredient(self, admin_client: TestClient, seed_ingredient):
        """Обновление ингредиента."""
        ing = seed_ingredient("Старое")
        resp = admin_client.put(f"/api/v1/ingredients/{ing.id}", json={"name": "Новое"})
        assert resp.status_code == 200
        assert resp.json()["name"] == "Новое"

    def test_update_ingredient_not_found(self, admin_client: TestClient):
        """Обновление несуществующего ингредиента → 404."""
        resp = admin_client.put("/api/v1/ingredients/9999", json={"name": "X"})
        assert resp.status_code == 404

    def test_delete_ingredient(self, admin_client: TestClient, seed_ingredient):
        """Удаление ингредиента."""
        ing = seed_ingredient("На удаление")
        resp = admin_client.delete(f"/api/v1/ingredients/{ing.id}")
        assert resp.status_code == 200

        resp2 = admin_client.get(f"/api/v1/ingredients/{ing.id}")
        assert resp2.status_code == 404

    def test_delete_ingredient_not_found(self, admin_client: TestClient):
        """Удаление несуществующего ингредиента → 404."""
        resp = admin_client.delete("/api/v1/ingredients/9999")
        assert resp.status_code == 404


# ───────────────────────── SEARCH ─────────────────────────
class TestIngredientSearch:
    """Тесты поиска ингредиентов."""

    def test_search_ingredients(self, admin_client: TestClient, seed_ingredient):
        """Поиск ингредиента по подстроке."""
        seed_ingredient("Помидор")
        seed_ingredient("Огурец")

        resp = admin_client.get("/api/v1/ingredients/search/", params={"q": "Помид"})
        assert resp.status_code == 200
        assert len(resp.json()) >= 1
        assert resp.json()[0]["name"] == "Помидор"

    def test_search_no_results(self, admin_client: TestClient):
        """Поиск без результатов."""
        resp = admin_client.get("/api/v1/ingredients/search/", params={"q": "zzznone"})
        assert resp.status_code == 200
        assert resp.json() == []


# ───────────────────────── ACCESS ─────────────────────────
class TestIngredientAccess:
    """Тесты контроля доступа к ингредиентам."""

    def test_waiter_can_read_ingredients(self, waiter_client: TestClient, seed_ingredient):
        """Официант может читать ингредиенты."""
        seed_ingredient("Тестовый")
        resp = waiter_client.get("/api/v1/ingredients/")
        assert resp.status_code == 200

    def test_waiter_cannot_create_ingredient(self, waiter_client: TestClient):
        """Официант не может создавать ингредиенты → 403."""
        resp = waiter_client.post("/api/v1/ingredients/", json={"name": "Нет"})
        assert resp.status_code == 403

    def test_waiter_cannot_delete_ingredient(self, waiter_client: TestClient, seed_ingredient):
        """Официант не может удалять ингредиенты → 403."""
        ing = seed_ingredient("Нельзя удалить")
        resp = waiter_client.delete(f"/api/v1/ingredients/{ing.id}")
        assert resp.status_code == 403

    def test_manager_can_create_ingredient(self, manager_client: TestClient):
        """Менеджер может создавать ингредиенты."""
        resp = manager_client.post("/api/v1/ingredients/", json={"name": "Менеджерский"})
        assert resp.status_code == 200
