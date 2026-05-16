"""
Тест корневого эндпоинта: GET /.
"""
from fastapi.testclient import TestClient
from app.main import app


def test_root_endpoint():
    """Корневой эндпоинт возвращает приветственное сообщение."""
    client = TestClient(app)
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json() == {"message": "Restaurant API"}
