"""
Тесты для эндпоинтов блюд: /api/v1/dishes.
"""
import pytest
from fastapi.testclient import TestClient


# ───────────────────────── CRUD ─────────────────────────
class TestDishCRUD:
    """CRUD-тесты для блюд."""

    def test_create_dish_without_ingredients(self, admin_client: TestClient):
        """Создание блюда без ингредиентов."""
        resp = admin_client.post("/api/v1/dishes/", json={
            "name": "Паста",
            "description": "Итальянская паста",
            "price": 450.0,
            "ingredient_ids": []
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "Паста"
        assert data["price"] == 450.0
        assert data["ingredients"] == []

    def test_create_dish_with_ingredients(self, admin_client: TestClient, seed_ingredient):
        """Создание блюда с ингредиентами."""
        ing1 = seed_ingredient("Мука")
        ing2 = seed_ingredient("Яйца")

        resp = admin_client.post("/api/v1/dishes/", json={
            "name": "Пельмени",
            "description": "Домашние пельмени",
            "price": 350.0,
            "ingredient_ids": [ing1.id, ing2.id]
        })
        assert resp.status_code == 200
        data = resp.json()
        assert set(data["ingredients"]) == {ing1.id, ing2.id}

    def test_create_dish_invalid_ingredient(self, admin_client: TestClient):
        """Создание блюда с несуществующим ингредиентом → 404."""
        resp = admin_client.post("/api/v1/dishes/", json={
            "name": "Бад",
            "price": 100.0,
            "ingredient_ids": [99999]
        })
        assert resp.status_code == 404

    def test_list_dishes(self, admin_client: TestClient, seed_dish):
        """Получение списка всех блюд."""
        seed_dish("Салат", 200.0)
        seed_dish("Суп", 300.0)

        resp = admin_client.get("/api/v1/dishes/")
        assert resp.status_code == 200
        assert len(resp.json()) >= 2

    def test_get_dish_by_id(self, admin_client: TestClient, seed_dish):
        """Получение блюда по ID."""
        dish = seed_dish("Стейк", 800.0)
        resp = admin_client.get(f"/api/v1/dishes/{dish.id}")
        assert resp.status_code == 200
        assert resp.json()["name"] == "Стейк"

    def test_get_dish_not_found(self, admin_client: TestClient):
        """Запрос несуществующего блюда → 404."""
        resp = admin_client.get("/api/v1/dishes/9999")
        assert resp.status_code == 404

    def test_update_dish_name(self, admin_client: TestClient, seed_dish):
        """Обновление названия блюда."""
        dish = seed_dish("Старое", 100.0)
        resp = admin_client.put(f"/api/v1/dishes/{dish.id}", json={
            "name": "Новое"
        })
        assert resp.status_code == 200
        assert resp.json()["name"] == "Новое"

    def test_update_dish_price(self, admin_client: TestClient, seed_dish):
        """Обновление цены блюда."""
        dish = seed_dish("Ценовое", 100.0)
        resp = admin_client.put(f"/api/v1/dishes/{dish.id}", json={
            "price": 999.0
        })
        assert resp.status_code == 200
        assert resp.json()["price"] == 999.0

    def test_update_dish_ingredients(self, admin_client: TestClient, seed_dish, seed_ingredient):
        """Обновление ингредиентов блюда."""
        dish = seed_dish("С ингредиентами", 500.0)
        ing = seed_ingredient("Новый ингредиент")
        resp = admin_client.put(f"/api/v1/dishes/{dish.id}", json={
            "ingredient_ids": [ing.id]
        })
        assert resp.status_code == 200
        assert ing.id in resp.json()["ingredients"]

    def test_update_dish_not_found(self, admin_client: TestClient):
        """Обновление несуществующего блюда → 404."""
        resp = admin_client.put("/api/v1/dishes/9999", json={"name": "X"})
        assert resp.status_code == 404

    def test_delete_dish(self, admin_client: TestClient, seed_dish):
        """Удаление блюда."""
        dish = seed_dish("Удаляемое", 100.0)
        resp = admin_client.delete(f"/api/v1/dishes/{dish.id}")
        assert resp.status_code == 200

        resp2 = admin_client.get(f"/api/v1/dishes/{dish.id}")
        assert resp2.status_code == 404

    def test_delete_dish_not_found(self, admin_client: TestClient):
        """Удаление несуществующего блюда → 404."""
        resp = admin_client.delete("/api/v1/dishes/9999")
        assert resp.status_code == 404


# ───────────────────────── SEARCH ─────────────────────────
class TestDishSearch:
    """Тесты поиска блюд."""

    def test_search_dishes(self, admin_client: TestClient, seed_dish):
        """Поиск блюд по подстроке."""
        seed_dish("Курица гриль", 550.0)
        seed_dish("Рыба гриль", 650.0)

        resp = admin_client.get("/api/v1/dishes/search/", params={"q": "гриль"})
        assert resp.status_code == 200
        assert len(resp.json()) >= 2

    def test_search_no_results(self, admin_client: TestClient):
        """Поиск без результатов."""
        resp = admin_client.get("/api/v1/dishes/search/", params={"q": "zzznone"})
        assert resp.status_code == 200
        assert resp.json() == []


# ───────────────────────── ACCESS ─────────────────────────
class TestDishAccess:
    """Тесты контроля доступа к блюдам."""

    def test_waiter_can_read_dishes(self, waiter_client: TestClient, seed_dish):
        """Официант может читать блюда."""
        seed_dish("Чтение", 100.0)
        resp = waiter_client.get("/api/v1/dishes/")
        assert resp.status_code == 200

    def test_waiter_cannot_create_dish(self, waiter_client: TestClient):
        """Официант не может создавать блюда → 403."""
        resp = waiter_client.post("/api/v1/dishes/", json={
            "name": "Нет", "price": 100.0
        })
        assert resp.status_code == 403

    def test_waiter_cannot_delete_dish(self, waiter_client: TestClient, seed_dish):
        """Официант не может удалять блюда → 403."""
        dish = seed_dish("Неудаляемое", 100.0)
        resp = waiter_client.delete(f"/api/v1/dishes/{dish.id}")
        assert resp.status_code == 403

    def test_manager_can_create_dish(self, manager_client: TestClient):
        """Менеджер может создавать блюда."""
        resp = manager_client.post("/api/v1/dishes/", json={
            "name": "Менеджерское", "price": 200.0
        })
        assert resp.status_code == 200
