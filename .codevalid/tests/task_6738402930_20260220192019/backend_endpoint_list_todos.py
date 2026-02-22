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

# Test Case 1: GET /todos returns empty list when no todos exist
def test_get_todos_returns_empty_list_when_no_todos_exist():
    response = client.get("/todos")
    assert response.status_code == 200
    assert response.json() == {"todos": []}

# Test Case 2: GET /todos returns a single todo with all fields
def test_get_todos_returns_single_todo_with_all_fields():
    todo_id = insert_todo(
        title="Buy groceries",
        description="Milk, eggs, bread",
        notes="Remember to check for discounts",
        expiry_date="2024-07-31"
    )
    response = client.get("/todos")
    assert response.status_code == 200
    assert response.json() == {
        "todos": [
            {
                "description": "Milk, eggs, bread",
                "expiry_date": "2024-07-31",
                "id": todo_id,
                "notes": "Remember to check for discounts",
                "title": "Buy groceries"
            }
        ]
    }

# Test Case 3: GET /todos returns multiple todo items
def test_get_todos_returns_multiple_todo_items():
    id1 = insert_todo(
        title="Buy groceries",
        description="Milk, eggs, bread",
        notes="Remember to check for discounts",
        expiry_date="2024-07-31"
    )
    id2 = insert_todo(
        title="Read book"
    )
    response = client.get("/todos")
    assert response.status_code == 200
    todos = response.json()["todos"]
    assert len(todos) == 2
    assert {
        "description": "Milk, eggs, bread",
        "expiry_date": "2024-07-31",
        "id": id1,
        "notes": "Remember to check for discounts",
        "title": "Buy groceries"
    } in todos
    assert {
        "description": None,
        "expiry_date": None,
        "id": id2,
        "notes": None,
        "title": "Read book"
    } in todos

# Test Case 4: GET /todos returns todos with absent optional fields
def test_get_todos_returns_todos_with_absent_optional_fields():
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

# Test Case 5: GET /todos returns expiry_date in correct format
def test_get_todos_returns_expiry_date_in_correct_format():
    todo_id = insert_todo(
        title="Finish project",
        expiry_date="2024-12-01"
    )
    response = client.get("/todos")
    assert response.status_code == 200
    assert response.json() == {
        "todos": [
            {
                "description": None,
                "expiry_date": "2024-12-01",
                "id": todo_id,
                "notes": None,
                "title": "Finish project"
            }
        ]
    }

# Test Case 6: GET /todos supports large number of todos
def test_get_todos_supports_large_number_of_todos():
    todos = []
    for i in range(1000):
        todo_id = insert_todo(title=f"Todo {i+1}")
        todos.append({
            "description": None,
            "expiry_date": None,
            "id": todo_id,
            "notes": None,
            "title": f"Todo {i+1}"
        })
    response = client.get("/todos")
    assert response.status_code == 200
    result = response.json()
    assert "todos" in result
    assert len(result["todos"]) == 1000
    # Check that all inserted todos are present
    for todo in todos:
        assert todo in result["todos"]

# Test Case 7: GET /todos with incorrect HTTP method
def test_get_todos_with_incorrect_http_method():
    response = client.post("/todos", json={})
    assert response.status_code == 405
    assert response.json() == {"error": "Method Not Allowed"}

# Test Case 8: GET /todos without Content-Type header
def test_get_todos_without_content_type_header():
    # FastAPI TestClient always sends Accept header, but we can omit Content-Type for GET
    response = client.get("/todos")
    assert response.status_code == 200
    assert response.json() == {"todos": []}

# Test Case 9: GET /todos returns todos with special characters
def test_get_todos_returns_todos_with_special_characters():
    todo_id = insert_todo(
        title="Call mom 💖",
        description="Check-in & update: 😊",
        notes="Don't forget: 🎂"
    )
    response = client.get("/todos")
    assert response.status_code == 200
    assert response.json() == {
        "todos": [
            {
                "description": "Check-in & update: 😊",
                "expiry_date": None,
                "id": todo_id,
                "notes": "Don't forget: 🎂",
                "title": "Call mom 💖"
            }
        ]
    }

# Test Case 10: GET /todos returns todos with maximum field lengths
def test_get_todos_returns_todos_with_maximum_field_lengths():
    max_title = "T" * 255
    max_description = "D" * 1000
    max_notes = "N" * 1000
    todo_id = insert_todo(
        title=max_title,
        description=max_description,
        notes=max_notes,
        expiry_date="2024-12-31"
    )
    response = client.get("/todos")
    assert response.status_code == 200
    assert response.json() == {
        "todos": [
            {
                "description": max_description,
                "expiry_date": "2024-12-31",
                "id": todo_id,
                "notes": max_notes,
                "title": max_title
            }
        ]
    }

# Test Case 11: GET /todos does not return deleted todo
def test_get_todos_does_not_return_deleted_todo():
    id1 = insert_todo(title="Active todo")
    id2 = insert_todo(title="Deleted todo")
    # Delete id2
    conn = sqlite3.connect(db.DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM todos WHERE id = ?", (id2,))
    conn.commit()
    conn.close()
    response = client.get("/todos")
    assert response.status_code == 200
    todos = response.json()["todos"]
    assert {
        "description": None,
        "expiry_date": None,
        "id": id1,
        "notes": None,
        "title": "Active todo"
    } in todos
    assert all(t["id"] != id2 for t in todos)