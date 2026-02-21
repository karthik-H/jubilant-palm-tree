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

def get_todo_by_id(todo_id):
    with db_cursor() as cur:
        cur.execute(
            "SELECT id, title, description, notes, expiry_date FROM todos WHERE id = ?",
            (todo_id,),
        )
        row = cur.fetchone()
        if row:
            return normalize_todo(dict(row))
        return None

# Test Case 1: Create Todo with only required field
def test_create_todo_with_only_required_field():
    resp = client.post("/todos", json={"title": "Buy groceries"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Buy groceries"
    assert data["description"] is None
    assert data["notes"] is None
    assert data["expiry_date"] is None
    assert isinstance(data["id"], int)

# Test Case 2: Create Todo with all valid fields
def test_create_todo_with_all_valid_fields():
    resp = client.post(
        "/todos",
        json={
            "title": "Read book",
            "description": "Finish reading 'Clean Code'",
            "notes": "Start from chapter 3",
            "expiry_date": "2024-12-31",
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Read book"
    assert data["description"] == "Finish reading 'Clean Code'"
    assert data["notes"] == "Start from chapter 3"
    assert data["expiry_date"] == "2024-12-31"
    assert isinstance(data["id"], int)

# Test Case 3: Create Todo missing required title
def test_create_todo_missing_required_title():
    resp = client.post(
        "/todos",
        json={"description": "No title", "notes": "Should fail"},
    )
    assert resp.status_code == 400
    assert resp.json()["detail"][0]["msg"] == "field required"
    assert resp.json()["detail"][0]["loc"][-1] == "title"

# Test Case 4: Create Todo with empty title
def test_create_todo_with_empty_title():
    resp = client.post("/todos", json={"title": ""})
    assert resp.status_code == 422 or resp.status_code == 400
    # FastAPI returns 422 for validation error
    if resp.status_code == 422:
        assert resp.json()["detail"][0]["msg"] == "ensure this value has at least 1 characters"
        assert resp.json()["detail"][0]["loc"][-1] == "title"
    else:
        assert resp.json()["error"] == "Title must not be empty."

# Test Case 5: Create Todo with invalid expiry_date format
def test_create_todo_with_invalid_expiry_date_format():
    resp = client.post(
        "/todos",
        json={"title": "Call mom", "expiry_date": "31-12-2024"},
    )
    assert resp.status_code == 422 or resp.status_code == 400
    # FastAPI returns 422 for invalid date format
    if resp.status_code == 422:
        assert resp.json()["detail"][0]["msg"].startswith("invalid date format")
        assert resp.json()["detail"][0]["loc"][-1] == "expiry_date"
    else:
        assert resp.json()["error"] == "expiry_date must match format 'YYYY-MM-DD'."

# Test Case 6: Create Todo with expiry_date explicitly null
def test_create_todo_with_explicitly_null_expiry_date():
    resp = client.post(
        "/todos",
        json={"title": "Walk dog", "expiry_date": None},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Walk dog"
    assert data["expiry_date"] is None

# Test Case 7: Create Todo with title at maximum length
def test_create_todo_with_title_at_max_length():
    max_title = "T" * 255
    resp = client.post("/todos", json={"title": max_title})
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == max_title
    assert data["description"] is None
    assert data["notes"] is None
    assert data["expiry_date"] is None

# Test Case 8: Create Todo with title of one character
def test_create_todo_with_title_of_one_character():
    resp = client.post("/todos", json={"title": "A"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "A"
    assert data["description"] is None
    assert data["notes"] is None
    assert data["expiry_date"] is None

# Test Case 9: Create Todo with expiry_date on leap year
def test_create_todo_with_expiry_date_on_leap_year():
    resp = client.post(
        "/todos",
        json={"title": "Leap year check", "expiry_date": "2024-02-29"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Leap year check"
    assert data["expiry_date"] == "2024-02-29"

# Test Case 10: List Todos when none exist
def test_list_todos_when_none_exist():
    resp = client.get("/todos")
    assert resp.status_code == 200
    assert resp.json() == []

# Test Case 11: List Todos after creation
def test_list_todos_after_creation():
    id1 = insert_todo("Buy groceries")
    id2 = insert_todo(
        "Read book",
        description="Finish reading 'Clean Code'",
        notes="Start from chapter 3",
        expiry_date="2024-12-31",
    )
    resp = client.get("/todos")
    assert resp.status_code == 200
    todos = resp.json()
    expected = [
        {
            "id": id1,
            "title": "Buy groceries",
            "description": None,
            "notes": None,
            "expiry_date": None,
        },
        {
            "id": id2,
            "title": "Read book",
            "description": "Finish reading 'Clean Code'",
            "notes": "Start from chapter 3",
            "expiry_date": "2024-12-31",
        },
    ]
    # Normalize response
    actual = [normalize_todo(todo) for todo in todos]
    assert actual == expected

# Test Case 12: Get Todo by valid id
def test_get_todo_by_valid_id():
    id1 = insert_todo("Buy groceries")
    resp = client.get(f"/todos/{id1}")
    assert resp.status_code == 200
    todo = normalize_todo(resp.json())
    expected = {
        "id": id1,
        "title": "Buy groceries",
        "description": None,
        "notes": None,
        "expiry_date": None,
    }
    assert todo == expected

# Test Case 13: Get Todo by nonexistent id
def test_get_todo_by_nonexistent_id():
    resp = client.get("/todos/99999")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Todo not found"

# Test Case 14: Update Todo with a single field
def test_update_todo_with_single_field():
    id1 = insert_todo("Buy groceries")
    resp = client.put(f"/todos/{id1}", json={"notes": "Remember to buy eggs"})
    assert resp.status_code == 200
    todo = normalize_todo(resp.json())
    expected = {
        "id": id1,
        "title": "Buy groceries",
        "description": None,
        "notes": "Remember to buy eggs",
        "expiry_date": None,
    }
    assert todo == expected

# Test Case 15: Update Todo with multiple fields
def test_update_todo_with_multiple_fields():
    id2 = insert_todo(
        "Read book",
        description="Finish reading 'Clean Code'",
        notes="Start from chapter 3",
        expiry_date="2024-12-31",
    )
    resp = client.put(
        f"/todos/{id2}",
        json={"description": "Read chapters 1-5", "expiry_date": "2024-11-30"},
    )
    assert resp.status_code == 200
    todo = normalize_todo(resp.json())
    expected = {
        "id": id2,
        "title": "Read book",
        "description": "Read chapters 1-5",
        "notes": "Start from chapter 3",
        "expiry_date": "2024-11-30",
    }
    assert todo == expected

# Test Case 16: Update Todo with invalid expiry_date format
def test_update_todo_with_invalid_expiry_date_format():
    id2 = insert_todo(
        "Read book",
        description="Finish reading 'Clean Code'",
        notes="Start from chapter 3",
        expiry_date="2024-12-31",
    )
    resp = client.put(
        f"/todos/{id2}",
        json={"expiry_date": "20241130"},
    )
    assert resp.status_code == 422 or resp.status_code == 400
    if resp.status_code == 422:
        assert resp.json()["detail"][0]["msg"].startswith("invalid date format")
        assert resp.json()["detail"][0]["loc"][-1] == "expiry_date"
    else:
        assert resp.json()["error"] == "expiry_date must match format 'YYYY-MM-DD'."

# Test Case 17: Update Todo by nonexistent id
def test_update_todo_by_nonexistent_id():
    resp = client.put("/todos/99999", json={"notes": "This won't update"})
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Todo not found"

# Test Case 18: Delete Todo by valid id
def test_delete_todo_by_valid_id():
    id1 = insert_todo("Buy groceries")
    resp = client.delete(f"/todos/{id1}")
    assert resp.status_code == 204
    # Confirm deleted
    resp2 = client.get(f"/todos/{id1}")
    assert resp2.status_code == 404

# Test Case 19: Delete Todo by nonexistent id
def test_delete_todo_by_nonexistent_id():
    resp = client.delete("/todos/99999")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Todo not found"