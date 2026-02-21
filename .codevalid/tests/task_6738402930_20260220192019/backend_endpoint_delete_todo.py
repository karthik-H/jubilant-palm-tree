import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.database import init_db, get_connection

@pytest.fixture(autouse=True)
def setup_db(tmp_path, monkeypatch):
    import backend.database
    backend.database.DB_PATH = tmp_path / "test_todos.db"
    init_db()
    yield

@pytest.fixture
def client():
    return TestClient(app)

def insert_todo(id, title="Sample", description="Desc", notes="Notes", expiry_date=None):
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO todos (id, title, description, notes, expiry_date) VALUES (?, ?, ?, ?, ?)",
            (id, title, description, notes, expiry_date)
        )
        conn.commit()

# Test Case 1: Delete existing todo successfully
def test_delete_existing_todo_successfully(client):
    insert_todo(1)
    resp = client.delete("/todos/1")
    assert resp.status_code == 204
    assert resp.content == b""
    resp2 = client.get("/todos/1")
    assert resp2.status_code == 404
    assert resp2.json() == {"detail": "Todo not found"}

# Test Case 2: Delete non-existent todo
def test_delete_non_existent_todo(client):
    resp = client.delete("/todos/9999")
    assert resp.status_code == 404
    assert resp.json() == {"detail": "Todo not found"}

# Test Case 3: Delete todo with non-integer ID (string)
def test_delete_todo_with_non_integer_id(client):
    resp = client.delete("/todos/abc")
    assert resp.status_code == 422
    detail = resp.json().get("detail")
    assert detail is not None
    # Accept custom error or FastAPI default validation error
    if isinstance(detail, str):
        assert detail == "Invalid todo_id format"
    else:
        assert any("value is not a valid integer" in str(item) or "Invalid todo_id format" in str(item) for item in detail)

# Test Case 4: Delete todo with negative ID
def test_delete_todo_with_negative_id(client):
    resp = client.delete("/todos/-1")
    assert resp.status_code == 404 or resp.status_code == 422
    if resp.status_code == 404:
        assert resp.json() == {"detail": "Todo not found"}
    else:
        detail = resp.json().get("detail")
        assert detail is not None
        if isinstance(detail, str):
            assert detail == "Invalid todo_id format"
        else:
            assert any("value is not a valid integer" in str(item) or "Invalid todo_id format" in str(item) for item in detail)

# Test Case 5: Delete todo with zero ID
def test_delete_todo_with_zero_id(client):
    resp = client.delete("/todos/0")
    assert resp.status_code == 404
    assert resp.json() == {"detail": "Todo not found"}

# Test Case 6: Delete same todo twice
def test_delete_same_todo_twice(client):
    insert_todo(2)
    resp1 = client.delete("/todos/2")
    assert resp1.status_code == 204
    assert resp1.content == b""
    resp2 = client.delete("/todos/2")
    assert resp2.status_code == 404
    assert resp2.json() == {"detail": "Todo not found"}

# Test Case 7: Delete todo with unexpected request body
def test_delete_todo_with_unexpected_request_body(client):
    insert_todo(3)
    resp = client.delete("/todos/3", json={"irrelevant": "data"})
    assert resp.status_code == 204
    assert resp.content == b""
    resp2 = client.get("/todos/3")
    assert resp2.status_code == 404
    assert resp2.json() == {"detail": "Todo not found"}

# Test Case 8: Delete todo with extremely large ID
def test_delete_todo_with_extremely_large_id(client):
    resp = client.delete("/todos/999999999999999999999999")
    assert resp.status_code == 404
    assert resp.json() == {"detail": "Todo not found"}

# Test Case 9: Delete todo with float ID
def test_delete_todo_with_float_id(client):
    resp = client.delete("/todos/1.5")
    assert resp.status_code == 422
    detail = resp.json().get("detail")
    assert detail is not None
    if isinstance(detail, str):
        assert detail == "Invalid todo_id format"
    else:
        assert any("value is not a valid integer" in str(item) or "Invalid todo_id format" in str(item) for item in detail)