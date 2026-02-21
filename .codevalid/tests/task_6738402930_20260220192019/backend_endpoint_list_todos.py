import pytest
from fastapi.testclient import TestClient
from backend.main import app
import backend.database as db
import sqlite3
import os

@pytest.fixture(autouse=True)
def setup_and_teardown_db(tmp_path, monkeypatch):
    # Use a temporary database for each test
    test_db_path = tmp_path / "test_todos.db"
    monkeypatch.setattr(db, "DB_PATH", str(test_db_path))
    # Initialize schema
    conn = sqlite3.connect(str(test_db_path))
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            notes TEXT,
            expiry_date TEXT
        )
    """)
    conn.commit()
    conn.close()
    yield
    # Cleanup
    if os.path.exists(test_db_path):
        os.remove(test_db_path)

client = TestClient(app)

def insert_todo(title, description=None, notes=None, expiry_date=None):
    conn = sqlite3.connect(db.DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO todos (title, description, notes, expiry_date) VALUES (?, ?, ?, ?)",
        (title, description, notes, expiry_date)
    )
    conn.commit()
    todo_id = cursor.lastrowid
    conn.close()
    return todo_id

# Test Case 1: List todos when database is empty
def test_list_todos_when_database_is_empty():
    response = client.get("/todos")
    assert response.status_code == 200
    assert response.json() == {"todos": []}

# Test Case 2: List todos when multiple todos exist
def test_list_todos_when_multiple_todos_exist():
    id1 = insert_todo(
        title="Buy groceries",
        description="Milk, eggs, bread",
        notes="Check for discounts",
        expiry_date="2024-07-01"
    )
    id2 = insert_todo(
        title="Call plumber"
    )
    response = client.get("/todos")
    assert response.status_code == 200
    todos = response.json()["todos"]
    assert len(todos) == 2
    assert {"description": "Milk, eggs, bread", "expiry_date": "2024-07-01", "id": id1, "notes": "Check for discounts", "title": "Buy groceries"} in todos
    assert {"description": None, "expiry_date": None, "id": id2, "notes": None, "title": "Call plumber"} in todos

# Test Case 3: Create todo with all valid fields
def test_create_todo_with_all_valid_fields():
    response = client.post(
        "/todos",
        json={
            "title": "Read book",
            "description": "Read 'Clean Code'",
            "notes": "Start with chapter 1",
            "expiry_date": "2024-06-30"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Read book"
    assert data["description"] == "Read 'Clean Code'"
    assert data["notes"] == "Start with chapter 1"
    assert data["expiry_date"] == "2024-06-30"
    assert isinstance(data["id"], int)

# Test Case 4: Create todo with only required field
def test_create_todo_with_only_required_field():
    response = client.post(
        "/todos",
        json={"title": "Walk the dog"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Walk the dog"
    assert data["description"] is None
    assert data["notes"] is None
    assert data["expiry_date"] is None
    assert isinstance(data["id"], int)

# Test Case 5: Create todo with empty title
def test_create_todo_with_empty_title():
    response = client.post(
        "/todos",
        json={"title": ""}
    )
    assert response.status_code == 400
    assert response.json() == {"error": "Title is required and cannot be empty."}

# Test Case 6: Create todo with missing title
def test_create_todo_with_missing_title():
    response = client.post(
        "/todos",
        json={"description": "No title"}
    )
    assert response.status_code == 400
    assert response.json() == {"error": "Title is required."}

# Test Case 7: Create todo with invalid expiry_date format
def test_create_todo_with_invalid_expiry_date_format():
    response = client.post(
        "/todos",
        json={"title": "Pay bills", "expiry_date": "30-06-2024"}
    )
    assert response.status_code == 400
    assert response.json() == {"error": "expiry_date must be in 'YYYY-MM-DD' format."}

# Test Case 8: Create todo with expiry_date on leap day
def test_create_todo_with_expiry_date_on_leap_day():
    response = client.post(
        "/todos",
        json={"title": "Leap Day Task", "expiry_date": "2024-02-29"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Leap Day Task"
    assert data["expiry_date"] == "2024-02-29"
    assert data["description"] is None
    assert data["notes"] is None
    assert isinstance(data["id"], int)

# Test Case 9: Create todo with expiry_date invalid month
def test_create_todo_with_expiry_date_invalid_month():
    response = client.post(
        "/todos",
        json={"title": "Impossible Month", "expiry_date": "2024-13-01"}
    )
    assert response.status_code == 400
    assert response.json() == {"error": "expiry_date must be a valid date in 'YYYY-MM-DD' format."}

# Test Case 10: Get todo by valid id
def test_get_todo_by_valid_id():
    todo_id = insert_todo(
        title="Buy groceries",
        description="Milk, eggs, bread",
        notes="Check for discounts",
        expiry_date="2024-07-01"
    )
    response = client.get(f"/todos/{todo_id}")
    assert response.status_code == 200
    assert response.json() == {
        "description": "Milk, eggs, bread",
        "expiry_date": "2024-07-01",
        "id": todo_id,
        "notes": "Check for discounts",
        "title": "Buy groceries"
    }

# Test Case 11: Get todo by nonexistent id
def test_get_todo_by_nonexistent_id():
    response = client.get("/todos/999")
    assert response.status_code == 404
    assert response.json() == {"error": "Todo not found."}

# Test Case 12: Update todo with some fields
def test_update_todo_with_some_fields():
    todo_id = insert_todo(
        title="Buy groceries",
        description="Milk, eggs, bread",
        notes="Check for discounts",
        expiry_date="2024-07-01"
    )
    response = client.put(
        f"/todos/{todo_id}",
        json={"description": "Updated description", "notes": "Updated notes"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == todo_id
    assert data["title"] == "Buy groceries"
    assert data["description"] == "Updated description"
    assert data["notes"] == "Updated notes"
    assert data["expiry_date"] == "2024-07-01"

# Test Case 13: Update todo with invalid expiry_date format
def test_update_todo_with_invalid_expiry_date_format():
    todo_id = insert_todo(
        title="Buy groceries",
        description="Milk, eggs, bread",
        notes="Check for discounts",
        expiry_date="2024-07-01"
    )
    response = client.put(
        f"/todos/{todo_id}",
        json={"expiry_date": "07/01/2024"}
    )
    assert response.status_code == 400
    assert response.json() == {"error": "expiry_date must be in 'YYYY-MM-DD' format."}

# Test Case 14: Update todo by nonexistent id
def test_update_todo_by_nonexistent_id():
    response = client.put(
        "/todos/999",
        json={"title": "New title"}
    )
    assert response.status_code == 404
    assert response.json() == {"error": "Todo not found."}

# Test Case 15: Delete todo by valid id
def test_delete_todo_by_valid_id():
    todo_id = insert_todo(
        title="Call plumber"
    )
    response = client.delete(f"/todos/{todo_id}")
    assert response.status_code == 204
    assert response.content == b""
    # Confirm deleted
    get_response = client.get(f"/todos/{todo_id}")
    assert get_response.status_code == 404
    # Confirm not in list
    list_response = client.get("/todos")
    todos = list_response.json()["todos"]
    assert all(t["id"] != todo_id for t in todos)

# Test Case 16: Delete todo by nonexistent id
def test_delete_todo_by_nonexistent_id():
    response = client.delete("/todos/999")
    assert response.status_code == 404
    assert response.json() == {"error": "Todo not found."}

# Test Case 17: List todos with null optional fields
def test_list_todos_with_null_optional_fields():
    todo_id = insert_todo(title="Walk the dog")
    response = client.get("/todos")
    assert response.status_code == 200
    assert response.json() == {
        "todos": [
            {
                "description": None,
                "expiry_date": None,
                "id": todo_id,
                "notes": None,
                "title": "Walk the dog"
            }
        ]
    }

# Test Case 18: Create todo with maximum title length
def test_create_todo_with_maximum_title_length():
    max_title = "T" * 255
    response = client.post(
        "/todos",
        json={"title": max_title}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == max_title
    assert data["description"] is None
    assert data["notes"] is None
    assert data["expiry_date"] is None
    assert isinstance(data["id"], int)