import os
import tempfile
import pytest
import sqlite3
from backend.database import db_cursor
from backend.main import app
from fastapi.testclient import TestClient

@pytest.fixture(scope="function")
def test_db_path():
    # Use a temporary file for the test database
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    os.remove(path)

@pytest.fixture(scope="function")
def override_db(test_db_path, monkeypatch):
    # Patch the database path used by db_cursor
    monkeypatch.setattr("backend.database.DB_PATH", test_db_path)
    yield

@pytest.fixture(scope="function")
def client(override_db):
    return TestClient(app)

def get_todo_id(client, title):
    resp = client.get("/todos")
    for todo in resp.json():
        if todo["title"] == title:
            return todo["id"]
    return None

# Test Case 1: Create todo with required title only
def test_create_todo_required_title_only(client):
    resp = client.post("/todos", json={"title": "Buy milk"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Buy milk"
    assert data["description"] is None
    assert data["expiry_date"] is None
    assert data["notes"] is None
    assert "id" in data

# Test Case 2: Create todo with all fields valid
def test_create_todo_all_fields_valid(client):
    payload = {
        "title": "Submit report",
        "description": "Quarterly financial report",
        "expiry_date": "2024-12-31",
        "notes": "Attach spreadsheets"
    }
    resp = client.post("/todos", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == payload["title"]
    assert data["description"] == payload["description"]
    assert data["expiry_date"] == payload["expiry_date"]
    assert data["notes"] == payload["notes"]
    assert "id" in data

# Test Case 3: Create todo missing required title
def test_create_todo_missing_title(client):
    resp = client.post("/todos", json={"description": "No title test"})
    assert resp.status_code == 400
    assert resp.json()["error"] == "Title is required"

# Test Case 4: Create todo with empty title
def test_create_todo_empty_title(client):
    resp = client.post("/todos", json={"title": ""})
    assert resp.status_code == 400
    assert resp.json()["error"] == "Title must be non-empty"

# Test Case 5: Create todo with invalid expiry_date format
def test_create_todo_invalid_expiry_date_format(client):
    resp = client.post("/todos", json={"title": "Invalid date", "expiry_date": "31-12-2024"})
    assert resp.status_code == 400
    assert resp.json()["error"] == "expiry_date must match 'YYYY-MM-DD'"

# Test Case 6: Create todo with expiry_date as empty string
def test_create_todo_expiry_date_empty_string(client):
    resp = client.post("/todos", json={"title": "Expiry empty", "expiry_date": ""})
    assert resp.status_code == 400
    assert resp.json()["error"] == "expiry_date must match 'YYYY-MM-DD'"

# Test Case 7: List all existing todos
def test_list_all_existing_todos(client):
    # Create two todos
    client.post("/todos", json={"title": "Buy milk"})
    client.post("/todos", json={
        "title": "Submit report",
        "description": "Quarterly financial report",
        "expiry_date": "2024-12-31",
        "notes": "Attach spreadsheets"
    })
    resp = client.get("/todos")
    assert resp.status_code == 200
    todos = resp.json()
    assert len(todos) >= 2
    titles = [todo["title"] for todo in todos]
    assert "Buy milk" in titles
    assert "Submit report" in titles

# Test Case 8: Get todo with valid id
def test_get_todo_with_valid_id(client):
    client.post("/todos", json={"title": "Buy milk"})
    todo_id = get_todo_id(client, "Buy milk")
    resp = client.get(f"/todos/{todo_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "Buy milk"
    assert data["description"] is None
    assert data["expiry_date"] is None
    assert data["notes"] is None
    assert data["id"] == todo_id

# Test Case 9: Get todo with nonexistent id
def test_get_todo_with_nonexistent_id(client):
    resp = client.get("/todos/invalid_id")
    assert resp.status_code == 404
    assert resp.json()["error"] == "Todo not found"

# Test Case 10: Update todo with partial fields
def test_update_todo_partial_fields(client):
    client.post("/todos", json={"title": "Buy milk"})
    todo_id = get_todo_id(client, "Buy milk")
    resp = client.patch(f"/todos/{todo_id}", json={"description": "Updated description"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["description"] == "Updated description"
    assert data["title"] == "Buy milk"
    assert data["expiry_date"] is None
    assert data["notes"] is None
    assert data["id"] == todo_id

# Test Case 11: Update todo with invalid expiry_date format
def test_update_todo_invalid_expiry_date_format(client):
    client.post("/todos", json={"title": "Buy milk"})
    todo_id = get_todo_id(client, "Buy milk")
    resp = client.patch(f"/todos/{todo_id}", json={"expiry_date": "2024/12/31"})
    assert resp.status_code == 400
    assert resp.json()["error"] == "expiry_date must match 'YYYY-MM-DD'"

# Test Case 12: Update todo with nonexistent id
def test_update_todo_nonexistent_id(client):
    resp = client.patch("/todos/invalid_id", json={"description": "Should not update"})
    assert resp.status_code == 404
    assert resp.json()["error"] == "Todo not found"

# Test Case 13: Delete todo with valid id
def test_delete_todo_with_valid_id(client):
    client.post("/todos", json={"title": "Buy milk"})
    client.post("/todos", json={
        "title": "Submit report",
        "description": "Quarterly financial report",
        "expiry_date": "2024-12-31",
        "notes": "Attach spreadsheets"
    })
    todo_id_1 = get_todo_id(client, "Buy milk")
    todo_id_2 = get_todo_id(client, "Submit report")
    resp = client.delete(f"/todos/{todo_id_2}")
    assert resp.status_code == 200
    assert resp.json()["message"] == "Todo deleted successfully"
    # Follow-up: GET deleted todo returns 404
    resp2 = client.get(f"/todos/{todo_id_2}")
    assert resp2.status_code == 404
    assert resp2.json()["error"] == "Todo not found"
    # Follow-up: GET /todos returns only todo_id_1
    resp3 = client.get("/todos")
    todos = resp3.json()
    ids = [todo["id"] for todo in todos]
    assert todo_id_1 in ids
    assert todo_id_2 not in ids

# Test Case 14: Delete todo with nonexistent id
def test_delete_todo_with_nonexistent_id(client):
    resp = client.delete("/todos/invalid_id")
    assert resp.status_code == 404
    assert resp.json()["error"] == "Todo not found"

# Test Case 15: Create todo with long title
def test_create_todo_with_long_title(client):
    long_title = "T" * 255
    resp = client.post("/todos", json={"title": long_title})
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == long_title
    assert data["description"] is None
    assert data["expiry_date"] is None
    assert data["notes"] is None
    assert "id" in data

# Test Case 16: Create todo with all optional fields explicitly null
def test_create_todo_optional_fields_null(client):
    resp = client.post("/todos", json={
        "title": "Test nulls",
        "description": None,
        "expiry_date": None,
        "notes": None
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Test nulls"
    assert data["description"] is None
    assert data["expiry_date"] is None
    assert data["notes"] is None
    assert "id" in data

# Test Case 17: Update todo with fields set to null
def test_update_todo_fields_set_to_null(client):
    client.post("/todos", json={
        "title": "Buy milk",
        "description": "desc",
        "expiry_date": "2024-12-31",
        "notes": "notes"
    })
    todo_id = get_todo_id(client, "Buy milk")
    resp = client.patch(f"/todos/{todo_id}", json={
        "description": None,
        "expiry_date": None,
        "notes": None
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["description"] is None
    assert data["expiry_date"] is None
    assert data["notes"] is None
    assert data["title"] == "Buy milk"
    assert data["id"] == todo_id

# Test Case 18: db_cursor commits transaction on successful CRUD
def test_db_cursor_commits_transaction(test_db_path, monkeypatch):
    monkeypatch.setattr("backend.database.DB_PATH", test_db_path)
    with db_cursor() as cursor:
        cursor.execute("CREATE TABLE todos (id INTEGER PRIMARY KEY, title TEXT)")
        cursor.execute("INSERT INTO todos (title) VALUES (?)", ("Buy milk",))
    # Check that the data is committed
    conn = sqlite3.connect(test_db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT title FROM todos")
    result = cursor.fetchone()
    assert result[0] == "Buy milk"
    conn.close()

# Test Case 19: db_cursor closes connection on context exit
def test_db_cursor_closes_connection(test_db_path, monkeypatch):
    monkeypatch.setattr("backend.database.DB_PATH", test_db_path)
    with db_cursor() as cursor:
        cursor.execute("CREATE TABLE todos (id INTEGER PRIMARY KEY, title TEXT)")
    # After context exit, connection should be closed
    # Try to use cursor after context exit should raise
    with db_cursor() as cursor:
        pass
    with pytest.raises(sqlite3.ProgrammingError):
        cursor.execute("SELECT 1")

# Test Case 20: db_cursor rolls back transaction on exception
def test_db_cursor_rolls_back_on_exception(test_db_path, monkeypatch):
    monkeypatch.setattr("backend.database.DB_PATH", test_db_path)
    try:
        with db_cursor() as cursor:
            cursor.execute("CREATE TABLE todos (id INTEGER PRIMARY KEY, title TEXT)")
            cursor.execute("INSERT INTO todos (title) VALUES (?)", ("Buy milk",))
            raise Exception("Simulated error")
    except Exception:
        pass
    # Check that no data is persisted
    conn = sqlite3.connect(test_db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='todos'")
    table = cursor.fetchone()
    if table:
        cursor.execute("SELECT COUNT(*) FROM todos")
        count = cursor.fetchone()[0]
        assert count == 0
    conn.close()