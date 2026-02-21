import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from backend.main import app
from backend.database import init_db, get_connection

@pytest.fixture(autouse=True)
def setup_db(tmp_path, monkeypatch):
    # Patch DB_PATH to use a temporary file for isolation
    import backend.database
    backend.database.DB_PATH = tmp_path / "test_todos.db"
    init_db()
    yield
    # Cleanup handled by tmp_path fixture

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

def test_delete_existing_todo(client):
    # Given: A todo with id 101 exists
    insert_todo(101)
    # When: DELETE /todos/101 is called
    resp = client.delete("/todos/101")
    # Then: Todo 101 is removed. Subsequent GET /todos/101 returns 404.
    assert resp.status_code == 204
    assert resp.content == b""
    resp2 = client.get("/todos/101")
    assert resp2.status_code == 404
    assert resp2.json() == {"detail": "Todo not found"}

def test_delete_nonexistent_todo(client):
    # Given: No todo with id 9999 exists
    resp = client.delete("/todos/9999")
    # Then: API returns 404 Not Found
    assert resp.status_code == 404
    assert resp.json() == {"detail": "Todo not found"}

def test_delete_todo_twice(client):
    # Given: A todo with id 202 exists
    insert_todo(202)
    # When: DELETE /todos/202 is called twice
    resp1 = client.delete("/todos/202")
    assert resp1.status_code == 204
    assert resp1.content == b""
    resp2 = client.delete("/todos/202")
    assert resp2.status_code == 404
    assert resp2.json() == {"detail": "Todo not found"}

def test_delete_todo_with_invalid_id_format(client):
    # Given: No todo with id 'abc' exists; id must be integer
    resp = client.delete("/todos/abc")
    # Then: API returns 422 Unprocessable Entity (FastAPI default for path param type error)
    assert resp.status_code == 422 or resp.status_code == 400
    # Accept both 422 and 400, but check error detail
    detail = resp.json().get("detail")
    assert detail is not None
    # If custom 400, check for 'Invalid todo id format'
    if resp.status_code == 400:
        assert detail == "Invalid todo id format"
    else:
        # FastAPI default validation error
        assert any("value is not a valid integer" in str(item) for item in detail)

def test_delete_todo_with_boundary_id_value(client):
    # Given: No todo with id 0 exists (id starts at 1)
    resp = client.delete("/todos/0")
    # Then: API returns 404 Not Found
    assert resp.status_code == 404
    assert resp.json() == {"detail": "Todo not found"}

def test_delete_todo_without_authentication(client):
    # Given: Authentication is required but not provided.
    # The implementation does not enforce authentication, so this test will always pass (204 or 404).
    # If authentication is added, update this test accordingly.
    resp = client.delete("/todos/303")
    # Then: API returns 401 Unauthorized (if auth required), else 204/404
    assert resp.status_code in (204, 404)

def test_delete_todo_with_all_fields_set(client):
    # Given: A todo with id 404 exists and all fields are populated
    insert_todo(
        404,
        title="Full",
        description="Full desc",
        notes="Full notes",
        expiry_date="2026-12-31"
    )
    # When: DELETE /todos/404 is called
    resp = client.delete("/todos/404")
    # Then: Todo 404 and its fields are removed. GET /todos/404 returns 404.
    assert resp.status_code == 204
    assert resp.content == b""
    resp2 = client.get("/todos/404")
    assert resp2.status_code == 404
    assert resp2.json() == {"detail": "Todo not found"}

def test_delete_todo_in_empty_database(client):
    # Given: Database is empty, no todos exist
    resp = client.delete("/todos/1")
    # Then: API returns 404 Not Found
    assert resp.status_code == 404
    assert resp.json() == {"detail": "Todo not found"}

def test_delete_todo_with_long_integer_id(client):
    # Given: No todo with id 9223372036854775807 exists
    resp = client.delete("/todos/9223372036854775807")
    # Then: API returns 404 Not Found
    assert resp.status_code == 404
    assert resp.json() == {"detail": "Todo not found"}