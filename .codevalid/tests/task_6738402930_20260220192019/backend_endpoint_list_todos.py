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

# Test Case 2: GET /todos returns all existing todos with fields
def test_get_todos_returns_all_existing_todos_with_fields():
    id1 = insert_todo(
        title="Buy groceries",
        description="Milk, eggs, bread",
        notes="Use discount coupons",
        expiry_date="2024-07-01"
    )
    id2 = insert_todo(
        title="Read book"
    )
    response = client.get("/todos")
    assert response.status_code == 200
    todos = response.json()["todos"]
    expected = [
        {
            "description": "Milk, eggs, bread",
            "expiry_date": "2024-07-01",
            "id": id1,
            "notes": "Use discount coupons",
            "title": "Buy groceries"
        },
        {
            "description": None,
            "expiry_date": None,
            "id": id2,
            "notes": None,
            "title": "Read book"
        }
    ]
    assert sorted(todos, key=lambda t: t["id"]) == sorted(expected, key=lambda t: t["id"])

# Test Case 3: POST /todos creates todo with only required title
def test_post_todos_creates_todo_with_only_required_title():
    response = client.post(
        "/todos",
        json={"title": "New Task"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "New Task"
    assert data["description"] is None
    assert data["notes"] is None
    assert data["expiry_date"] is None
    assert isinstance(data["id"], int)

# Test Case 4: POST /todos creates todo with all fields valid
def test_post_todos_creates_todo_with_all_fields_valid():
    payload = {
        "description": "Quarterly business analysis",
        "expiry_date": "2024-07-15",
        "notes": "Finalize by Friday",
        "title": "Prepare report"
    }
    response = client.post("/todos", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == payload["title"]
    assert data["description"] == payload["description"]
    assert data["notes"] == payload["notes"]
    assert data["expiry_date"] == payload["expiry_date"]
    assert isinstance(data["id"], int)

# Test Case 5: POST /todos error when title is missing
def test_post_todos_error_when_title_is_missing():
    response = client.post(
        "/todos",
        json={"description": "Missing title"}
    )
    assert response.status_code == 400
    assert response.json() == {"error": "Title is required."}

# Test Case 6: POST /todos error when title is empty
def test_post_todos_error_when_title_is_empty():
    response = client.post(
        "/todos",
        json={"title": ""}
    )
    assert response.status_code == 400
    assert response.json() == {"error": "Title must not be empty."}

# Test Case 7: POST /todos error when expiry_date is invalid
def test_post_todos_error_when_expiry_date_is_invalid():
    response = client.post(
        "/todos",
        json={"expiry_date": "07-15-2024", "title": "Task"}
    )
    assert response.status_code == 400
    assert response.json() == {"error": "expiry_date must match 'YYYY-MM-DD'."}

# Test Case 8: POST /todos creates todo with expiry_date at boundary
def test_post_todos_creates_todo_with_expiry_date_at_boundary():
    response = client.post(
        "/todos",
        json={"expiry_date": "0000-01-01", "title": "Boundary date task"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Boundary date task"
    assert data["expiry_date"] == "0000-01-01"
    assert data["description"] is None
    assert data["notes"] is None
    assert isinstance(data["id"], int)

# Test Case 9: POST /todos creates todo with very long title
def test_post_todos_creates_todo_with_very_long_title():
    long_title = "T" * 255
    response = client.post(
        "/todos",
        json={"title": long_title}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == long_title
    assert data["description"] is None
    assert data["notes"] is None
    assert data["expiry_date"] is None
    assert isinstance(data["id"], int)

# Test Case 10: GET /todos/{id} returns todo with all fields
def test_get_todos_id_returns_todo_with_all_fields():
    todo_id = insert_todo(
        title="Buy groceries",
        description="Milk, eggs, bread",
        notes="Use discount coupons",
        expiry_date="2024-07-01"
    )
    response = client.get(f"/todos/{todo_id}")
    assert response.status_code == 200
    assert response.json() == {
        "description": "Milk, eggs, bread",
        "expiry_date": "2024-07-01",
        "id": todo_id,
        "notes": "Use discount coupons",
        "title": "Buy groceries"
    }

# Test Case 11: GET /todos/{id} returns error for nonexistent id
def test_get_todos_id_returns_error_for_nonexistent_id():
    response = client.get("/todos/9999")
    assert response.status_code == 404
    assert response.json() == {"error": "Todo not found."}

# Test Case 12: PUT /todos/{id} updates only specified fields
def test_put_todos_id_updates_only_specified_fields():
    todo_id = insert_todo(
        title="Buy groceries",
        description="Milk, eggs, bread",
        notes="Use discount coupons",
        expiry_date="2024-07-01"
    )
    response = client.put(
        f"/todos/{todo_id}",
        json={"description": "Updated description"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == todo_id
    assert data["title"] == "Buy groceries"
    assert data["description"] == "Updated description"
    assert data["notes"] == "Use discount coupons"
    assert data["expiry_date"] == "2024-07-01"

# Test Case 13: PUT /todos/{id} updates all fields
def test_put_todos_id_updates_all_fields():
    todo_id = insert_todo(
        title="Buy groceries",
        description="Milk, eggs, bread",
        notes="Use discount coupons",
        expiry_date="2024-07-01"
    )
    payload = {
        "description": "Get vegetables",
        "expiry_date": "2024-07-15",
        "notes": "Check prices",
        "title": "Shop groceries"
    }
    response = client.put(
        f"/todos/{todo_id}",
        json=payload
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == todo_id
    assert data["title"] == payload["title"]
    assert data["description"] == payload["description"]
    assert data["notes"] == payload["notes"]
    assert data["expiry_date"] == payload["expiry_date"]

# Test Case 14: PUT /todos/{id} error for invalid expiry_date
def test_put_todos_id_error_for_invalid_expiry_date():
    todo_id = insert_todo(
        title="Buy groceries",
        description="Milk, eggs, bread",
        notes="Use discount coupons",
        expiry_date="2024-07-01"
    )
    response = client.put(
        f"/todos/{todo_id}",
        json={"expiry_date": "20240715"}
    )
    assert response.status_code == 400
    assert response.json() == {"error": "expiry_date must match 'YYYY-MM-DD'."}

# Test Case 15: PUT /todos/{id} error for nonexistent todo id
def test_put_todos_id_error_for_nonexistent_todo_id():
    response = client.put(
        "/todos/9999",
        json={"title": "Nonexistent"}
    )
    assert response.status_code == 404
    assert response.json() == {"error": "Todo not found."}

# Test Case 16: DELETE /todos/{id} removes todo successfully
def test_delete_todos_id_removes_todo_successfully():
    todo_id = insert_todo(
        title="Buy groceries",
        description="Milk, eggs, bread",
        notes="Use discount coupons",
        expiry_date="2024-07-01"
    )
    response = client.delete(f"/todos/{todo_id}")
    assert response.status_code == 204
    assert response.content == b""
    # Confirm deleted
    get_response = client.get(f"/todos/{todo_id}")
    assert get_response.status_code == 404

# Test Case 17: DELETE /todos/{id} error for nonexistent todo id
def test_delete_todos_id_error_for_nonexistent_todo_id():
    response = client.delete("/todos/9999")
    assert response.status_code == 404
    assert response.json() == {"error": "Todo not found."}

# Test Case 18: POST /todos creates todo with notes as empty string
def test_post_todos_creates_todo_with_notes_as_empty_string():
    response = client.post(
        "/todos",
        json={"notes": "", "title": "Task with empty notes"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Task with empty notes"
    assert data["notes"] == ""
    assert data["description"] is None
    assert data["expiry_date"] is None
    assert isinstance(data["id"], int)

# Test Case 19: POST /todos creates todo with description as empty string
def test_post_todos_creates_todo_with_description_as_empty_string():
    response = client.post(
        "/todos",
        json={"description": "", "title": "Task with empty description"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Task with empty description"
    assert data["description"] == ""
    assert data["notes"] is None
    assert data["expiry_date"] is None
    assert isinstance(data["id"], int)

# Test Case 20: GET /todos does not return deleted todo
def test_get_todos_does_not_return_deleted_todo():
    id1 = insert_todo(
        title="Buy groceries",
        description="Milk, eggs, bread",
        notes="Use discount coupons",
        expiry_date="2024-07-01"
    )
    id2 = insert_todo(
        title="Read book"
    )
    # Delete id1
    response = client.delete(f"/todos/{id1}")
    assert response.status_code == 204
    # List todos, should only return id2
    list_response = client.get("/todos")
    assert list_response.status_code == 200
    todos = list_response.json()["todos"]
    expected = [
        {
            "description": None,
            "expiry_date": None,
            "id": id2,
            "notes": None,
            "title": "Read book"
        }
    ]
    assert todos == expected