"""
Тесты для эндпоинтов заказов: /api/v1/orders.
"""
import pytest
from fastapi.testclient import TestClient


# ───────────────────────── CRUD ─────────────────────────
class TestOrderCRUD:
    """CRUD-тесты для заказов."""

    def test_create_order(self, admin_client: TestClient, seed_dish):
        """Создание заказа с позициями."""
        dish = seed_dish("Заказное блюдо", 500.0)

        resp = admin_client.post("/api/v1/orders/", json={
            "table_number": 5,
            "items": [
                {"dish_id": dish.id, "quantity": 2}
            ]
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["table_number"] == 5
        assert data["total_price"] == 1000.0  # 500 * 2
        assert len(data["items"]) == 1
        assert data["items"][0]["quantity"] == 2

    def test_create_order_with_client(self, admin_client: TestClient, seed_dish, seed_client):
        """Создание заказа с клиентом."""
        dish = seed_dish("С клиентом", 300.0)
        client = seed_client()

        resp = admin_client.post("/api/v1/orders/", json={
            "table_number": 3,
            "client_id": client.id,
            "items": [
                {"dish_id": dish.id, "quantity": 1}
            ]
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["client_id"] == client.id
        assert data["total_price"] == 300.0

    def test_create_order_multiple_items(self, admin_client: TestClient, seed_dish):
        """Создание заказа с несколькими позициями."""
        d1 = seed_dish("Блюдо А", 200.0)
        d2 = seed_dish("Блюдо Б", 350.0)

        resp = admin_client.post("/api/v1/orders/", json={
            "table_number": 1,
            "items": [
                {"dish_id": d1.id, "quantity": 2},
                {"dish_id": d2.id, "quantity": 1},
            ]
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_price"] == 750.0  # 200*2 + 350*1
        assert len(data["items"]) == 2

    def test_create_order_invalid_dish(self, admin_client: TestClient):
        """Создание заказа с несуществующим блюдом → 404."""
        resp = admin_client.post("/api/v1/orders/", json={
            "table_number": 1,
            "items": [
                {"dish_id": 99999, "quantity": 1}
            ]
        })
        assert resp.status_code == 404

    def test_create_order_invalid_client(self, admin_client: TestClient, seed_dish):
        """Создание заказа с несуществующим клиентом → 404."""
        dish = seed_dish("Клиент404", 100.0)
        resp = admin_client.post("/api/v1/orders/", json={
            "table_number": 1,
            "client_id": 99999,
            "items": [
                {"dish_id": dish.id, "quantity": 1}
            ]
        })
        assert resp.status_code == 404

    def test_list_orders(self, admin_client: TestClient, seed_dish):
        """Получение списка всех заказов."""
        dish = seed_dish("Листовое", 100.0)
        admin_client.post("/api/v1/orders/", json={
            "table_number": 1,
            "items": [{"dish_id": dish.id, "quantity": 1}]
        })

        resp = admin_client.get("/api/v1/orders/")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)
        assert len(resp.json()) >= 1

    def test_get_order_by_id(self, admin_client: TestClient, seed_dish):
        """Получение заказа по ID."""
        dish = seed_dish("По ID", 100.0)
        create_resp = admin_client.post("/api/v1/orders/", json={
            "table_number": 2,
            "items": [{"dish_id": dish.id, "quantity": 1}]
        })
        order_id = create_resp.json()["id"]

        resp = admin_client.get(f"/api/v1/orders/{order_id}")
        assert resp.status_code == 200
        assert resp.json()["table_number"] == 2

    def test_get_order_not_found(self, admin_client: TestClient):
        """Запрос несуществующего заказа → 404."""
        resp = admin_client.get("/api/v1/orders/9999")
        assert resp.status_code == 404

    def test_update_order(self, admin_client: TestClient, seed_dish, seed_client):
        """Обновление заказа (номер стола и клиент)."""
        dish = seed_dish("Обновляемое", 100.0)
        client = seed_client()
        create_resp = admin_client.post("/api/v1/orders/", json={
            "table_number": 1,
            "items": [{"dish_id": dish.id, "quantity": 1}]
        })
        order_id = create_resp.json()["id"]

        resp = admin_client.put(f"/api/v1/orders/{order_id}", json={
            "table_number": 10,
            "client_id": client.id
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["table_number"] == 10
        assert data["client_id"] == client.id

    def test_update_order_not_found(self, admin_client: TestClient):
        """Обновление несуществующего заказа → 404."""
        resp = admin_client.put("/api/v1/orders/9999", json={"table_number": 5})
        assert resp.status_code == 404

    def test_update_order_invalid_client(self, admin_client: TestClient, seed_dish):
        """Обновление заказа с несуществующим клиентом → 404."""
        dish = seed_dish("Клиент404 UPD", 100.0)
        create_resp = admin_client.post("/api/v1/orders/", json={
            "table_number": 1,
            "items": [{"dish_id": dish.id, "quantity": 1}]
        })
        order_id = create_resp.json()["id"]

        resp = admin_client.put(f"/api/v1/orders/{order_id}", json={
            "client_id": 99999
        })
        assert resp.status_code == 404

    def test_delete_order(self, admin_client: TestClient, seed_dish):
        """Удаление заказа."""
        dish = seed_dish("Удаляемое", 100.0)
        create_resp = admin_client.post("/api/v1/orders/", json={
            "table_number": 1,
            "items": [{"dish_id": dish.id, "quantity": 1}]
        })
        order_id = create_resp.json()["id"]

        resp = admin_client.delete(f"/api/v1/orders/{order_id}")
        assert resp.status_code == 200

        resp2 = admin_client.get(f"/api/v1/orders/{order_id}")
        assert resp2.status_code == 404

    def test_delete_order_not_found(self, admin_client: TestClient):
        """Удаление несуществующего заказа → 404."""
        resp = admin_client.delete("/api/v1/orders/9999")
        assert resp.status_code == 404


# ───────────────────────── ACCESS ─────────────────────────
class TestOrderAccess:
    """Тесты контроля доступа к заказам."""

    def test_waiter_can_create_order(self, waiter_client: TestClient, seed_dish):
        """Официант может создавать заказы."""
        dish = seed_dish("Официантское", 100.0)
        resp = waiter_client.post("/api/v1/orders/", json={
            "table_number": 7,
            "items": [{"dish_id": dish.id, "quantity": 1}]
        })
        assert resp.status_code == 200

    def test_waiter_can_read_orders(self, waiter_client: TestClient):
        """Официант может читать заказы."""
        resp = waiter_client.get("/api/v1/orders/")
        assert resp.status_code == 200

    def test_waiter_cannot_update_order(self, waiter_client: TestClient, seed_dish, db_session):
        """Официант не может обновлять заказы → 403."""
        from app.models.order import Order
        from app.models.order_item import OrderItem

        dish = seed_dish("ВейтерНоАпдейт", 100.0)
        order = Order(table_number=1, total_price=100.0)
        db_session.add(order)
        db_session.commit()
        db_session.refresh(order)
        db_session.add(OrderItem(order_id=order.id, dish_id=dish.id, quantity=1, price=100.0))
        db_session.commit()

        resp = waiter_client.put(f"/api/v1/orders/{order.id}", json={
            "table_number": 99
        })
        assert resp.status_code == 403

    def test_waiter_cannot_delete_order(self, waiter_client: TestClient, seed_dish, db_session):
        """Официант не может удалять заказы → 403."""
        from app.models.order import Order
        from app.models.order_item import OrderItem

        dish = seed_dish("ВейтерНоДелит", 100.0)
        order = Order(table_number=1, total_price=100.0)
        db_session.add(order)
        db_session.commit()
        db_session.refresh(order)
        db_session.add(OrderItem(order_id=order.id, dish_id=dish.id, quantity=1, price=100.0))
        db_session.commit()

        resp = waiter_client.delete(f"/api/v1/orders/{order.id}")
        assert resp.status_code == 403
