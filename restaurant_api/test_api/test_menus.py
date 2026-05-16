"""
Тесты для эндпоинтов меню: /api/v1/menus.
"""
import pytest
from fastapi.testclient import TestClient

from app.models.menu import Menu
from app.models.menu_item import MenuItem


# ───────────────────────── CRUD ─────────────────────────
class TestMenuCRUD:
    """CRUD-тесты для меню."""

    def test_create_menu_empty(self, admin_client: TestClient):
        """Создание пустого меню (без блюд)."""
        resp = admin_client.post("/api/v1/menus/", json={
            "name": "Завтраки",
            "dish_ids": []
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "Завтраки"
        assert data["items"] == []

    def test_create_menu_with_dishes(self, admin_client: TestClient, seed_dish):
        """Создание меню с блюдами."""
        d1 = seed_dish("Блюдо1", 100.0)
        d2 = seed_dish("Блюдо2", 200.0)

        resp = admin_client.post("/api/v1/menus/", json={
            "name": "Обеды",
            "dish_ids": [d1.id, d2.id]
        })
        assert resp.status_code == 200
        data = resp.json()
        assert set(data["items"]) == {d1.id, d2.id}

    def test_create_menu_invalid_dish(self, admin_client: TestClient):
        """Создание меню с несуществующим блюдом → 404."""
        resp = admin_client.post("/api/v1/menus/", json={
            "name": "Плохое",
            "dish_ids": [99999]
        })
        assert resp.status_code == 404

    def test_list_menus(self, admin_client: TestClient, db_session):
        """Получение списка всех меню."""
        db_session.add(Menu(name="Menu A"))
        db_session.add(Menu(name="Menu B"))
        db_session.commit()

        resp = admin_client.get("/api/v1/menus/")
        assert resp.status_code == 200
        assert len(resp.json()) >= 2

    def test_get_menu_by_id(self, admin_client: TestClient, db_session):
        """Получение меню по ID."""
        menu = Menu(name="Тестовое меню")
        db_session.add(menu)
        db_session.commit()
        db_session.refresh(menu)

        resp = admin_client.get(f"/api/v1/menus/{menu.id}")
        assert resp.status_code == 200
        assert resp.json()["name"] == "Тестовое меню"

    def test_get_menu_not_found(self, admin_client: TestClient):
        """Запрос несуществующего меню → 404."""
        resp = admin_client.get("/api/v1/menus/9999")
        assert resp.status_code == 404

    def test_update_menu_name(self, admin_client: TestClient, db_session):
        """Обновление названия меню."""
        menu = Menu(name="Старое")
        db_session.add(menu)
        db_session.commit()
        db_session.refresh(menu)

        resp = admin_client.put(f"/api/v1/menus/{menu.id}", json={
            "name": "Новое"
        })
        assert resp.status_code == 200
        assert resp.json()["name"] == "Новое"

    def test_update_menu_dishes(self, admin_client: TestClient, db_session, seed_dish):
        """Обновление состава блюд в меню."""
        menu = Menu(name="Меню с блюдами")
        db_session.add(menu)
        db_session.commit()
        db_session.refresh(menu)

        d = seed_dish("Новое блюдо", 300.0)
        resp = admin_client.put(f"/api/v1/menus/{menu.id}", json={
            "dish_ids": [d.id]
        })
        assert resp.status_code == 200
        assert d.id in resp.json()["items"]

    def test_update_menu_not_found(self, admin_client: TestClient):
        """Обновление несуществующего меню → 404."""
        resp = admin_client.put("/api/v1/menus/9999", json={"name": "X"})
        assert resp.status_code == 404

    def test_delete_menu(self, admin_client: TestClient, db_session):
        """Удаление меню."""
        menu = Menu(name="Удаляемое")
        db_session.add(menu)
        db_session.commit()
        db_session.refresh(menu)

        resp = admin_client.delete(f"/api/v1/menus/{menu.id}")
        assert resp.status_code == 200

        resp2 = admin_client.get(f"/api/v1/menus/{menu.id}")
        assert resp2.status_code == 404

    def test_delete_menu_not_found(self, admin_client: TestClient):
        """Удаление несуществующего меню → 404."""
        resp = admin_client.delete("/api/v1/menus/9999")
        assert resp.status_code == 404


# ───────────────────────── SEARCH ─────────────────────────
class TestMenuSearch:
    """Тесты поиска меню."""

    def test_search_menus(self, admin_client: TestClient, db_session):
        """Поиск меню по подстроке."""
        db_session.add(Menu(name="Барная карта"))
        db_session.add(Menu(name="Детское меню"))
        db_session.commit()

        resp = admin_client.get("/api/v1/menus/search/", params={"q": "Барная"})
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

    def test_search_no_results(self, admin_client: TestClient):
        """Поиск без результатов."""
        resp = admin_client.get("/api/v1/menus/search/", params={"q": "zzznone"})
        assert resp.status_code == 200
        assert resp.json() == []


# ───────────────────────── EXPORT ─────────────────────────
class TestMenuExport:
    """Тесты экспорта меню в DOCX/XLSX."""

    def test_export_docx(self, admin_client: TestClient, db_session, seed_dish):
        """Экспорт меню в DOCX."""
        menu = Menu(name="Экспорт DOCX")
        db_session.add(menu)
        db_session.commit()
        db_session.refresh(menu)

        d = seed_dish("Экспортное блюдо", 250.0)
        db_session.add(MenuItem(menu_id=menu.id, dish_id=d.id))
        db_session.commit()

        resp = admin_client.get(f"/api/v1/menus/{menu.id}/export/docx")
        assert resp.status_code == 200
        assert "application/vnd.openxmlformats" in resp.headers.get("content-type", "")

    def test_export_xlsx(self, admin_client: TestClient, db_session, seed_dish):
        """Экспорт меню в XLSX."""
        menu = Menu(name="Экспорт XLSX")
        db_session.add(menu)
        db_session.commit()
        db_session.refresh(menu)

        d = seed_dish("Ещё блюдо", 300.0)
        db_session.add(MenuItem(menu_id=menu.id, dish_id=d.id))
        db_session.commit()

        resp = admin_client.get(f"/api/v1/menus/{menu.id}/export/xlsx")
        assert resp.status_code == 200
        assert "spreadsheetml" in resp.headers.get("content-type", "")


# ───────────────────────── ACCESS ─────────────────────────
class TestMenuAccess:
    """Тесты контроля доступа к меню."""

    def test_waiter_can_read_menus(self, waiter_client: TestClient, db_session):
        """Официант может читать меню."""
        db_session.add(Menu(name="Для чтения"))
        db_session.commit()
        resp = waiter_client.get("/api/v1/menus/")
        assert resp.status_code == 200

    def test_waiter_cannot_create_menu(self, waiter_client: TestClient):
        """Официант не может создавать меню → 403."""
        resp = waiter_client.post("/api/v1/menus/", json={"name": "Нет"})
        assert resp.status_code == 403

    def test_waiter_cannot_delete_menu(self, waiter_client: TestClient, db_session):
        """Официант не может удалять меню → 403."""
        menu = Menu(name="Нельзя удалить")
        db_session.add(menu)
        db_session.commit()
        db_session.refresh(menu)
        resp = waiter_client.delete(f"/api/v1/menus/{menu.id}")
        assert resp.status_code == 403
