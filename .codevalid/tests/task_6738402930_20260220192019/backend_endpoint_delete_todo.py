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

# Test Case 1: Delete existing todo by valid ID
def test_delete_existing_todo_by_valid_id(client):
    insert_todo(1)
    resp = client.delete("/todos/1")
    assert resp.status_code == 204
    assert resp.content == b""
    # GET /todos/1 returns 404
    resp2 = client.get("/todos/1")
    assert resp2.status_code == 404
    assert resp2.json() == {"detail": "Todo not found"}
    # The todo is not listed in GET /todos
    resp3 = client.get("/todos")
    todos = resp3.json()
    assert all(todo["id"] != 1 for todo in todos)

# Test Case 2: Delete non-existent todo returns 404
def test_delete_nonexistent_todo_returns_404(client):
    resp = client.delete("/todos/999999")
    assert resp.status_code == 404
    assert resp.json() == {"detail": "Todo not found"}

# Test Case 3: Delete todo with invalid string ID returns 404
def test_delete_todo_with_invalid_string_id_returns_404(client):
    resp = client.delete("/todos/abc")
    # Accept 404 (preferred) or validation error (422)
    assert resp.status_code in (404, 422)
    if resp.status_code == 404:
        assert resp.json() == {"detail": "Todo not found"}
    else:
        # FastAPI default validation error
        detail = resp.json().get("detail")
        assert detail is not None
        assert any("value is not a valid integer" in str(item) for item in detail)

# Test Case 4: Delete todo with minimum valid ID (1)
def test_delete_todo_with_minimum_valid_id(client):
    insert_todo(1)
    resp = client.delete("/todos/1")
    assert resp.status_code == 204
    assert resp.content == b""
    resp2 = client.get("/todos/1")
    assert resp2.status_code == 404
    assert resp2.json() == {"detail": "Todo not found"}

# Test Case 5: Delete todo with maximum integer ID
def test_delete_todo_with_maximum_integer_id(client):
    resp = client.delete("/todos/2147483647")
    assert resp.status_code == 404
    assert resp.json() == {"detail": "Todo not found"}

# Test Case 6: Delete already deleted todo returns 404
def test_delete_already_deleted_todo_returns_404(client):
    insert_todo(2)
    resp1 = client.delete("/todos/2")
    assert resp1.status_code == 204
    assert resp1.content == b""
    resp2 = client.delete("/todos/2")
    assert resp2.status_code == 404
    assert resp2.json() == {"detail": "Todo not found"}

# Test Case 7: Delete todo without Content-Type header
def test_delete_todo_without_content_type_header(client):
    insert_todo(3)
    # DELETE without Content-Type header (body is empty)
    resp = client.delete("/todos/3")
    assert resp.status_code == 204
    assert resp.content == b""
    resp2 = client.get("/todos/3")
    assert resp2.status_code == 404
    assert resp2.json() == {"detail": "Todo not found"}

# Test Case 8: Delete todo with unnecessary JSON body (should ignore body)
def test_delete_todo_with_unnecessary_json_body(client):
    insert_todo(4)
    resp = client.delete("/todos/4", json={"irrelevant": "data"})
    assert resp.status_code == 204
    assert resp.content == b""
    resp2 = client.get("/todos/4")
    assert resp2.status_code == 404
    assert resp2.json() == {"detail": "Todo not found"}

# Test Case 9: Delete todo and recreate with same title
def test_delete_todo_and_recreate_with_same_title(client):
    insert_todo(5, title="Test")
    resp = client.delete("/todos/5")
    assert resp.status_code == 204
    assert resp.content == b""
    # Recreate with same title
    resp2 = client.post("/todos", json={"title": "Test"})
    assert resp2.status_code == 201
    new_todo = resp2.json()
    assert new_todo["title"] == "Test"
    assert new_todo["id"] != 5
    # GET /todos/5 returns 404
    resp3 = client.get("/todos/5")
    assert resp3.status_code == 404
    assert resp3.json() == {"detail": "Todo not found"}

# Test Case 10: Delete todo with ID having leading zeros
def test_delete_todo_with_id_leading_zeros(client):
    insert_todo(1)
    resp = client.delete("/todos/00001")
    assert resp.status_code == 204
    assert resp.content == b""
    resp2 = client.get("/todos/1")
    assert resp2.status_code == 404
    assert resp2.json() == {"detail": "Todo not found"}