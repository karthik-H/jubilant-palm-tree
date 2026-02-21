import os
import shutil
import sqlite3
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from backend.database import init_db, DB_PATH
from backend.main import app

@pytest.fixture(autouse=True)
def isolate_db(tmp_path, monkeypatch):
    """Isolate the database for each test."""
    test_db = tmp_path / "test_todos.db"
    monkeypatch.setattr("backend.database.DB_PATH", test_db)
    yield
    if test_db.exists():
        test_db.unlink()

client = TestClient(app)

def get_db_schema(db_path):
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute("PRAGMA table_info(todos)")
        return cur.fetchall()

def get_todo_count():
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM todos")
        return cur.fetchone()[0]

# Test Case 1: Successful Database and Table Initialization
def test_successful_database_and_table_initialization():
    if DB_PATH.exists():
        DB_PATH.unlink()
    init_db()
    assert DB_PATH.exists()
    schema = get_db_schema(DB_PATH)
    col_names = [col[1] for col in schema]
    assert "id" in col_names
    assert "title" in col_names
    assert "description" in col_names
    assert "notes" in col_names
    assert "expiry_date" in col_names

# Test Case 2: Idempotent Table Initialization
def test_idempotent_table_initialization():
    init_db()
    init_db()
    schema = get_db_schema(DB_PATH)
    assert len(schema) >= 5  # No duplicate columns

# Test Case 3: Create Todo with Only Required Title
def test_create_todo_with_only_required_title():
    init_db()
    response = client.post("/todos", json={"title": "Buy milk"})
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Buy milk"
    assert data["description"] == ""
    assert data["notes"] == ""
    assert data["expiry_date"] is None

# Test Case 4: Create Todo with All Fields
def test_create_todo_with_all_fields():
    init_db()
    payload = {
        "title": "Call Bob",
        "description": "Discuss project",
        "notes": "Urgent",
        "expiry_date": "2024-07-01"
    }
    response = client.post("/todos", json=payload)
    assert response.status_code == 201
    data = response.json()
    for k in payload:
        if k == "expiry_date":
            assert data[k] == payload[k]
        else:
            assert data[k] == payload[k]

# Test Case 5: Create Todo Missing Required Title
def test_create_todo_missing_required_title():
    init_db()
    response = client.post("/todos", json={"description": "No title"})
    assert response.status_code == 422
    assert "title" in response.text

# Test Case 6: Create Todo with Empty Title
def test_create_todo_with_empty_title():
    init_db()
    response = client.post("/todos", json={"title": "", "description": "Empty title"})
    assert response.status_code == 422
    assert "title" in response.text

# Test Case 7: Create Todo with Invalid Expiry Date Format
def test_create_todo_with_invalid_expiry_date_format():
    init_db()
    response = client.post("/todos", json={"title": "Renew license", "expiry_date": "07/01/2024"})
    assert response.status_code == 422
    assert "expiry_date" in response.text

# Test Case 8: Create Todo with Edge Case Expiry Date
def test_create_todo_with_edge_case_expiry_date():
    init_db()
    response = client.post("/todos", json={"title": "Leap year task", "expiry_date": "2024-02-29"})
    assert response.status_code == 201
    data = response.json()
    assert data["expiry_date"] == "2024-02-29"

# Test Case 9: List Todos When None Exist
def test_list_todos_when_none_exist():
    init_db()
    response = client.get("/todos")
    assert response.status_code == 200
    assert response.json() == []

# Test Case 10: List Todos When Multiple Exist
def test_list_todos_when_multiple_exist():
    init_db()
    todos = [
        {"title": "A", "description": "desc1"},
        {"title": "B", "notes": "note2"},
        {"title": "C", "expiry_date": "2024-12-31"}
    ]
    for todo in todos:
        client.post("/todos", json=todo)
    response = client.get("/todos")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    for i, todo in enumerate(todos):
        assert data[i]["title"] == todo["title"]

# Test Case 11: Get Todo by Valid ID
def test_get_todo_by_valid_id():
    init_db()
    response = client.post("/todos", json={"title": "Get me"})
    todo_id = response.json()["id"]
    response = client.get(f"/todos/{todo_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Get me"

# Test Case 12: Get Todo with Nonexistent ID
def test_get_todo_with_nonexistent_id():
    init_db()
    response = client.get("/todos/999")
    assert response.status_code == 404
    assert "not found" in response.text.lower()

# Test Case 13: Update Todo with Partial Fields
def test_update_todo_with_partial_fields():
    init_db()
    response = client.post("/todos", json={"title": "Partial"})
    todo_id = response.json()["id"]
    response = client.put(f"/todos/{todo_id}", json={"description": "Updated desc"})
    assert response.status_code == 200
    data = response.json()
    assert data["description"] == "Updated desc"
    assert data["title"] == "Partial"

# Test Case 14: Update Todo with All Fields
def test_update_todo_with_all_fields():
    init_db()
    response = client.post("/todos", json={"title": "Old", "description": "Old Desc", "notes": "Old Note", "expiry_date": "2024-01-01"})
    todo_id = response.json()["id"]
    payload = {
        "title": "New Title",
        "description": "New Desc",
        "notes": "New Note",
        "expiry_date": "2024-08-15"
    }
    response = client.put(f"/todos/{todo_id}", json=payload)
    assert response.status_code == 200
    data = response.json()
    for k in payload:
        if k == "expiry_date":
            assert data[k] == payload[k]
        else:
            assert data[k] == payload[k]

# Test Case 15: Update Todo with Invalid Expiry Date
def test_update_todo_with_invalid_expiry_date():
    init_db()
    response = client.post("/todos", json={"title": "Invalid update"})
    todo_id = response.json()["id"]
    response = client.put(f"/todos/{todo_id}", json={"expiry_date": "2024-8-5"})
    assert response.status_code == 422
    assert "expiry_date" in response.text

# Test Case 16: Update Nonexistent Todo
def test_update_nonexistent_todo():
    init_db()
    response = client.put("/todos/999", json={"title": "Should not work"})
    assert response.status_code == 404
    assert "not found" in response.text.lower()

# Test Case 17: Delete Todo by Valid ID
def test_delete_todo_by_valid_id():
    init_db()
    response = client.post("/todos", json={"title": "Delete me"})
    todo_id = response.json()["id"]
    response = client.delete(f"/todos/{todo_id}")
    assert response.status_code == 204
    # Confirm it's gone
    response = client.get(f"/todos/{todo_id}")
    assert response.status_code == 404

# Test Case 18: Delete Todo with Nonexistent ID
def test_delete_todo_with_nonexistent_id():
    init_db()
    response = client.delete("/todos/999")
    assert response.status_code == 404
    assert "not found" in response.text.lower()

# Test Case 19: Create Todo with Expiry Date Boundary Format
def test_create_todo_with_expiry_date_boundary_format():
    init_db()
    response = client.post("/todos", json={"title": "End of year", "expiry_date": "2024-12-31"})
    assert response.status_code == 201
    data = response.json()
    assert data["expiry_date"] == "2024-12-31"

# Test Case 20: Create Todo with Long Title
def test_create_todo_with_long_title():
    init_db()
    long_title = "T" * 255
    response = client.post("/todos", json={"title": long_title})
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == long_title

# Test Case 21: Create Todo with Special Characters in Title
def test_create_todo_with_special_characters_in_title():
    init_db()
    special_title = "@#&!*_()[]{}"
    response = client.post("/todos", json={"title": special_title})
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == special_title