import sqlite3
import pytest
import main
from fastapi.testclient import TestClient


@pytest.fixture
def client(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"  # Keep test data separate from real expenses.

    def test_connect():
        db = sqlite3.connect(db_path)
        db.row_factory = sqlite3.Row
        return db

    with test_connect() as db:
        db.execute(
            "CREATE TABLE expenses "
            "(id INTEGER PRIMARY KEY, description TEXT, amount REAL)"
        )

    monkeypatch.setattr(main, "connect", test_connect)
    with TestClient(main.app) as test_client:
        yield test_client


def test_add_list_and_delete(client):
    response = client.post("/expenses", json={"description": "Lunch", "amount": 12.5})
    assert response.status_code == 201
    expense_id = response.json()["id"]

    response = client.get("/expenses")
    assert response.status_code == 200
    assert response.json()[0]["description"] == "Lunch"

    response = client.delete(f"/expenses/{expense_id}")
    assert response.status_code == 200
    assert client.get("/expenses").json() == []


def test_invalid_amount(client):
    response = client.post("/expenses", json={"description": "Lunch", "amount": -1})
    assert response.status_code == 422
