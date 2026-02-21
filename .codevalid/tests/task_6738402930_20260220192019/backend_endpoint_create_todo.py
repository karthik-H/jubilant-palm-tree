import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.database import init_db, db_cursor

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    # Reset DB before each test
    init_db()
    with db_cursor() as cur:
        cur.execute("DELETE FROM todos")

def insert_todo(title, description=None, notes=None, expiry_date=None):
    with db_cursor() as cur:
        cur.execute(
            """
            INSERT INTO todos (title, description, notes, expiry_date)
            VALUES (?, ?, ?, ?)
            """,
            (
                title,
                description if description is not None else "",
                notes if notes is not None else "",
                expiry_date,
            ),
        )
        return cur.lastrowid

def normalize_todo(todo):
    # Convert empty strings to None for description/notes to match test expectations
    return {
        "id": todo["id"],
        "title": todo["title"],
        "description": todo["description"] if todo["description"] else None,
        "notes": todo["notes"] if todo["notes"] else None,
        "expiry_date": todo["expiry_date"] if todo["expiry_date"] else None,
    }

# Test Case 1: Create todo with all valid fields
def test_create_todo_with_all_valid_fields():
    resp = client.post(
        "/todos",
        json={
            "title": "Buy groceries",
            "description": "Milk, eggs, bread",
            "notes": "Use discount coupons",
            "expiry_date": "2024-09-01",
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Buy groceries"
    assert data["description"] == "Milk, eggs, bread"
    assert data["notes"] == "Use discount coupons"
    assert data["expiry_date"] == "2024-09-01"
    assert isinstance(data["id"], int)

# Test Case 2: Create todo with only required field
def test_create_todo_with_only_required_field():
    resp = client.post("/todos", json={"title": "Read a book"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Read a book"
    assert data["description"] is None
    assert data["notes"] is None
    assert data["expiry_date"] is None
    assert isinstance(data["id"], int)

# Test Case 3: Create todo with empty title
def test_create_todo_with_empty_title():
    resp = client.post("/todos", json={"title": ""})
    assert resp.status_code == 400
    assert resp.json()["error"] == "Title cannot be empty."

# Test Case 4: Create todo missing title
def test_create_todo_missing_title():
    resp = client.post("/todos", json={"description": "Task without title"})
    assert resp.status_code == 400
    assert resp.json()["error"] == "Title is required."

# Test Case 5: Create todo with invalid expiry_date format
def test_create_todo_with_invalid_expiry_date_format():
    resp = client.post(
        "/todos",
        json={"expiry_date": "2024/09/01", "title": "Finish homework"},
    )
    assert resp.status_code == 400
    assert resp.json()["error"] == "expiry_date must match format YYYY-MM-DD."

# Test Case 6: Create todo with expiry_date on leap day
def test_create_todo_with_expiry_date_on_leap_day():
    resp = client.post(
        "/todos",
        json={"expiry_date": "2024-02-29", "title": "Leap Year Task"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Leap Year Task"
    assert data["description"] is None
    assert data["notes"] is None
    assert data["expiry_date"] == "2024-02-29"
    assert isinstance(data["id"], int)

# Test Case 7: Create todo with long title
def test_create_todo_with_long_title():
    long_title = "T" * 255
    resp = client.post("/todos", json={"title": long_title})
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == long_title
    assert data["description"] is None
    assert data["notes"] is None
    assert data["expiry_date"] is None
    assert isinstance(data["id"], int)

# Test Case 8: Create todo with description and notes explicitly null
def test_create_todo_with_description_and_notes_null():
    resp = client.post(
        "/todos",
        json={"description": None, "notes": None, "title": "Null fields"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Null fields"
    assert data["description"] is None
    assert data["notes"] is None
    assert data["expiry_date"] is None
    assert isinstance(data["id"], int)

# Test Case 9: List all todos
def test_list_all_todos():
    # Create two todos as in previous test cases
    resp1 = client.post(
        "/todos",
        json={
            "title": "Buy groceries",
            "description": "Milk, eggs, bread",
            "notes": "Use discount coupons",
            "expiry_date": "2024-09-01",
        },
    )
    todo1 = resp1.json()
    resp2 = client.post("/todos", json={"title": "Read a book"})
    todo2 = resp2.json()
    resp = client.get("/todos")
    assert resp.status_code == 200
    todos = resp.json()
    expected = [
        {
            "description": "Milk, eggs, bread",
            "expiry_date": "2024-09-01",
            "id": todo1["id"],
            "notes": "Use discount coupons",
            "title": "Buy groceries",
        },
        {
            "description": None,
            "expiry_date": None,
            "id": todo2["id"],
            "notes": None,
            "title": "Read a book",
        },
    ]
    assert todos == expected

# Test Case 10: Get todo by valid id
def test_get_todo_by_valid_id():
    resp = client.post(
        "/todos",
        json={
            "title": "Buy groceries",
            "description": "Milk, eggs, bread",
            "notes": "Use discount coupons",
            "expiry_date": "2024-09-01",
        },
    )
    todo = resp.json()
    resp2 = client.get(f"/todos/{todo['id']}")
    assert resp2.status_code == 200
    assert resp2.json() == {
        "description": "Milk, eggs, bread",
        "expiry_date": "2024-09-01",
        "id": todo["id"],
        "notes": "Use discount coupons",
        "title": "Buy groceries",
    }

# Test Case 11: Get todo by non-existent id
def test_get_todo_by_non_existent_id():
    resp = client.get("/todos/999")
    assert resp.status_code == 404
    assert resp.json()["error"] == "Todo not found."

# Test Case 12: Update todo title only
def test_update_todo_title_only():
    resp = client.post(
        "/todos",
        json={
            "title": "Buy groceries",
            "description": "Milk, eggs, bread",
            "notes": "Use discount coupons",
            "expiry_date": "2024-09-01",
        },
    )
    todo = resp.json()
    resp2 = client.put(
        f"/todos/{todo['id']}",
        json={"title": "Buy groceries and snacks"},
    )
    assert resp2.status_code == 200
    assert resp2.json() == {
        "description": "Milk, eggs, bread",
        "expiry_date": "2024-09-01",
        "id": todo["id"],
        "notes": "Use discount coupons",
        "title": "Buy groceries and snacks",
    }

# Test Case 13: Update multiple fields of todo
def test_update_multiple_fields_of_todo():
    resp = client.post("/todos", json={"title": "Read a book"})
    todo = resp.json()
    resp2 = client.put(
        f"/todos/{todo['id']}",
        json={
            "description": "Science and history",
            "expiry_date": "2024-12-31",
            "title": "Read two books",
        },
    )
    assert resp2.status_code == 200
    assert resp2.json() == {
        "description": "Science and history",
        "expiry_date": "2024-12-31",
        "id": todo["id"],
        "notes": None,
        "title": "Read two books",
    }

# Test Case 14: Update todo with invalid expiry_date
def test_update_todo_with_invalid_expiry_date():
    resp = client.post(
        "/todos",
        json={
            "title": "Buy groceries",
            "description": "Milk, eggs, bread",
            "notes": "Use discount coupons",
            "expiry_date": "2024-09-01",
        },
    )
    todo = resp.json()
    resp2 = client.put(
        f"/todos/{todo['id']}",
        json={"expiry_date": "31-12-2024"},
    )
    assert resp2.status_code == 400
    assert resp2.json()["error"] == "expiry_date must match format YYYY-MM-DD."

# Test Case 15: Update todo with non-existent id
def test_update_todo_with_non_existent_id():
    resp = client.put("/todos/999", json={"title": "Ghost task"})
    assert resp.status_code == 404
    assert resp.json()["error"] == "Todo not found."

# Test Case 16: Delete todo by valid id
def test_delete_todo_by_valid_id():
    resp = client.post("/todos", json={"title": "Read a book"})
    todo = resp.json()
    resp2 = client.delete(f"/todos/{todo['id']}")
    assert resp2.status_code == 204
    # Confirm deleted
    resp3 = client.get(f"/todos/{todo['id']}")
    assert resp3.status_code == 404
    assert resp3.json()["error"] == "Todo not found."

# Test Case 17: Delete todo with non-existent id
def test_delete_todo_with_non_existent_id():
    resp = client.delete("/todos/999")
    assert resp.status_code == 404
    assert resp.json()["error"] == "Todo not found."

# Test Case 18: Access todo after deletion
def test_access_todo_after_deletion():
    resp = client.post("/todos", json={"title": "Read a book"})
    todo = resp.json()
    resp2 = client.delete(f"/todos/{todo['id']}")
    assert resp2.status_code == 204
    resp3 = client.get(f"/todos/{todo['id']}")
    assert resp3.status_code == 404
    assert resp3.json()["error"] == "Todo not found."

# Test Case 19: Create todo with expiry_date invalid month/day
def test_create_todo_with_expiry_date_invalid_month_day():
    resp = client.post(
        "/todos",
        json={"expiry_date": "2024-13-01", "title": "Invalid month"},
    )
    assert resp.status_code == 400
    assert resp.json()["error"] == "expiry_date must match format YYYY-MM-DD."

# Test Case 20: Create todo with expiry_date as non-string
def test_create_todo_with_expiry_date_as_non_string():
    resp = client.post(
        "/todos",
        json={"expiry_date": 20240901, "title": "Numeric expiry"},
    )
    assert resp.status_code == 400
    assert resp.json()["error"] == "expiry_date must be a string matching format YYYY-MM-DD."

# Test Case 21: Update notes field to null
def test_update_notes_field_to_null():
    resp = client.post(
        "/todos",
        json={
            "title": "Buy groceries",
            "description": "Milk, eggs, bread",
            "notes": "Use discount coupons",
            "expiry_date": "2024-09-01",
        },
    )
    todo = resp.json()
    # Update title first to match previous test state
    client.put(
        f"/todos/{todo['id']}",
        json={"title": "Buy groceries and snacks"},
    )
    resp2 = client.put(
        f"/todos/{todo['id']}",
        json={"notes": None},
    )
    assert resp2.status_code == 200
    assert resp2.json() == {
        "description": "Milk, eggs, bread",
        "expiry_date": "2024-09-01",
        "id": todo["id"],
        "notes": None,
        "title": "Buy groceries and snacks",
    }