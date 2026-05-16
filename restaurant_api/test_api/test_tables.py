"""
Тесты для эндпоинтов назначений столов: /api/v1/tables.
"""
import pytest
from fastapi.testclient import TestClient

from app.models.employee import Employee
from app.models.role import Role
from app.models.table_assignment import TableAssignment
from app.core.security import hash_password


# ───────────────────────── HELPERS ─────────────────────────
@pytest.fixture()
def waiter_employee(db_session):
    """Создаёт сотрудника-официанта (role_id=3) для тестов столов."""
    # Создаём роль официанта, если не существует
    role = db_session.query(Role).filter(Role.id == 3).first()
    if not role:
        role = Role(id=3, name="waiter_tbl", description="Официант")
        db_session.add(role)
        db_session.commit()
        db_session.refresh(role)

    emp = Employee(
        first_name="Официант",
        last_name="Тестовый",
        patronymic="",
        username="waiter_table_test",
        password_hash=hash_password("pass"),
        role_id=3,
        phone="+79001111111",
    )
    db_session.add(emp)
    db_session.commit()
    db_session.refresh(emp)
    return emp


@pytest.fixture()
def non_waiter_employee(db_session):
    """Создаёт сотрудника НЕ-официанта (role_id=1) для негативных тестов."""
    role = db_session.query(Role).filter(Role.id == 1).first()
    if not role:
        role = Role(id=1, name="admin_tbl", description="Администратор")
        db_session.add(role)
        db_session.commit()

    emp = Employee(
        first_name="Админ",
        last_name="Тестовый",
        patronymic="",
        username="admin_table_test",
        password_hash=hash_password("pass"),
        role_id=1,
        phone="+79002222222",
    )
    db_session.add(emp)
    db_session.commit()
    db_session.refresh(emp)
    return emp


# ───────────────────────── CRUD ─────────────────────────
class TestTableAssignmentCRUD:
    """CRUD-тесты для назначений столов."""

    def test_create_assignment(self, admin_client: TestClient, waiter_employee):
        """Создание назначения стола официанту."""
        resp = admin_client.post("/api/v1/tables/", json={
            "table_number": 1,
            "employee_id": waiter_employee.id
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["table_number"] == 1
        assert data["employee_id"] == waiter_employee.id
        assert "id" in data

    def test_create_assignment_non_waiter(self, admin_client: TestClient, non_waiter_employee):
        """Назначение стола не-официанту → 400."""
        resp = admin_client.post("/api/v1/tables/", json={
            "table_number": 2,
            "employee_id": non_waiter_employee.id
        })
        assert resp.status_code == 400

    def test_create_assignment_employee_not_found(self, admin_client: TestClient):
        """Назначение стола несуществующему сотруднику → 404."""
        resp = admin_client.post("/api/v1/tables/", json={
            "table_number": 3,
            "employee_id": 99999
        })
        assert resp.status_code == 404

    def test_list_assignments(self, admin_client: TestClient, waiter_employee, db_session):
        """Получение списка всех назначений."""
        db_session.add(TableAssignment(table_number=10, employee_id=waiter_employee.id))
        db_session.add(TableAssignment(table_number=11, employee_id=waiter_employee.id))
        db_session.commit()

        resp = admin_client.get("/api/v1/tables/")
        assert resp.status_code == 200
        assert len(resp.json()) >= 2

    def test_get_assignment_by_id(self, admin_client: TestClient, waiter_employee, db_session):
        """Получение назначения по ID."""
        assignment = TableAssignment(table_number=5, employee_id=waiter_employee.id)
        db_session.add(assignment)
        db_session.commit()
        db_session.refresh(assignment)

        resp = admin_client.get(f"/api/v1/tables/{assignment.id}")
        assert resp.status_code == 200
        assert resp.json()["table_number"] == 5

    def test_get_assignment_not_found(self, admin_client: TestClient):
        """Запрос несуществующего назначения → 404."""
        resp = admin_client.get("/api/v1/tables/9999")
        assert resp.status_code == 404

    def test_update_assignment(self, admin_client: TestClient, waiter_employee, db_session):
        """Обновление назначения стола."""
        assignment = TableAssignment(table_number=1, employee_id=waiter_employee.id)
        db_session.add(assignment)
        db_session.commit()
        db_session.refresh(assignment)

        resp = admin_client.put(f"/api/v1/tables/{assignment.id}", json={
            "table_number": 99,
            "employee_id": waiter_employee.id
        })
        assert resp.status_code == 200
        assert resp.json()["table_number"] == 99

    def test_update_assignment_not_found(self, admin_client: TestClient, waiter_employee):
        """Обновление несуществующего назначения → 404."""
        resp = admin_client.put("/api/v1/tables/9999", json={
            "table_number": 1,
            "employee_id": waiter_employee.id
        })
        assert resp.status_code == 404

    def test_update_assignment_non_waiter(self, admin_client: TestClient, waiter_employee, non_waiter_employee, db_session):
        """Обновление назначения с не-официантом → 400."""
        assignment = TableAssignment(table_number=1, employee_id=waiter_employee.id)
        db_session.add(assignment)
        db_session.commit()
        db_session.refresh(assignment)

        resp = admin_client.put(f"/api/v1/tables/{assignment.id}", json={
            "table_number": 1,
            "employee_id": non_waiter_employee.id
        })
        assert resp.status_code == 400

    def test_update_assignment_employee_not_found(self, admin_client: TestClient, waiter_employee, db_session):
        """Обновление назначения с несуществующим сотрудником → 404."""
        assignment = TableAssignment(table_number=1, employee_id=waiter_employee.id)
        db_session.add(assignment)
        db_session.commit()
        db_session.refresh(assignment)

        resp = admin_client.put(f"/api/v1/tables/{assignment.id}", json={
            "table_number": 1,
            "employee_id": 99999
        })
        assert resp.status_code == 404

    def test_delete_assignment(self, admin_client: TestClient, waiter_employee, db_session):
        """Удаление назначения стола."""
        assignment = TableAssignment(table_number=7, employee_id=waiter_employee.id)
        db_session.add(assignment)
        db_session.commit()
        db_session.refresh(assignment)

        resp = admin_client.delete(f"/api/v1/tables/{assignment.id}")
        assert resp.status_code == 200

        resp2 = admin_client.get(f"/api/v1/tables/{assignment.id}")
        assert resp2.status_code == 404

    def test_delete_assignment_not_found(self, admin_client: TestClient):
        """Удаление несуществующего назначения → 404."""
        resp = admin_client.delete("/api/v1/tables/9999")
        assert resp.status_code == 404


# ───────────────────────── ACCESS ─────────────────────────
class TestTableAssignmentAccess:
    """Тесты контроля доступа к назначениям столов."""

    def test_waiter_can_read_assignments(self, waiter_client: TestClient):
        """Официант может читать назначения."""
        resp = waiter_client.get("/api/v1/tables/")
        assert resp.status_code == 200

    def test_waiter_cannot_create_assignment(self, waiter_client: TestClient, waiter_employee):
        """Официант не может создавать назначения → 403."""
        resp = waiter_client.post("/api/v1/tables/", json={
            "table_number": 1,
            "employee_id": waiter_employee.id
        })
        assert resp.status_code == 403

    def test_waiter_cannot_delete_assignment(self, waiter_client: TestClient, waiter_employee, db_session):
        """Официант не может удалять назначения → 403."""
        assignment = TableAssignment(table_number=1, employee_id=waiter_employee.id)
        db_session.add(assignment)
        db_session.commit()
        db_session.refresh(assignment)

        resp = waiter_client.delete(f"/api/v1/tables/{assignment.id}")
        assert resp.status_code == 403

    def test_manager_can_create_assignment(self, manager_client: TestClient, waiter_employee):
        """Менеджер может создавать назначения."""
        resp = manager_client.post("/api/v1/tables/", json={
            "table_number": 15,
            "employee_id": waiter_employee.id
        })
        assert resp.status_code == 200
