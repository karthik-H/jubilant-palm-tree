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
                description if description is not None else None,
                notes if notes is not None else None,
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

# Test Case 1: Create todo with only required title
def test_create_todo_with_only_required_title():
    resp = client.post("/todos", json={"title": "Buy groceries"})
    assert resp.status_code == 201
    data = resp.json()
    assert data == {
        "id": data["id"],
        "title": "Buy groceries",
        "description": None,
        "notes": None,
        "expiry_date": None,
    }
    assert isinstance(data["id"], int)

# Test Case 2: Create todo with all fields provided
def test_create_todo_with_all_fields_provided():
    resp = client.post(
        "/todos",
        json={
            "title": "Submit report",
            "description": "Quarterly financial report",
            "notes": "Attach all receipts",
            "expiry_date": "2024-08-15",
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data == {
        "id": data["id"],
        "title": "Submit report",
        "description": "Quarterly financial report",
        "notes": "Attach all receipts",
        "expiry_date": "2024-08-15",
    }
    assert isinstance(data["id"], int)

# Test Case 3: Create todo with missing title
def test_create_todo_with_missing_title():
    resp = client.post(
        "/todos",
        json={"description": "No title field", "notes": "Should fail"},
    )
    assert resp.status_code == 400
    assert resp.json() == {"detail": "Title is required."}

# Test Case 4: Create todo with empty title
def test_create_todo_with_empty_title():
    resp = client.post(
        "/todos",
        json={"description": "Empty title test", "title": ""},
    )
    assert resp.status_code == 400
    assert resp.json() == {"detail": "Title must be non-empty."}

# Test Case 5: Create todo with invalid expiry_date format
def test_create_todo_with_invalid_expiry_date_format():
    resp = client.post(
        "/todos",
        json={"expiry_date": "15/08/2024", "title": "Bad expiry"},
    )
    assert resp.status_code == 400
    assert resp.json() == {"detail": "expiry_date must match format 'YYYY-MM-DD'."}

# Test Case 6: Create todo with expiry_date at boundary (valid)
def test_create_todo_with_expiry_date_at_boundary_valid():
    resp = client.post(
        "/todos",
        json={"expiry_date": "1900-01-01", "title": "Edge expiry"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data == {
        "id": data["id"],
        "title": "Edge expiry",
        "description": None,
        "notes": None,
        "expiry_date": "1900-01-01",
    }
    assert isinstance(data["id"], int)

# Test Case 7: Create todo with expiry_date year not four digits
def test_create_todo_with_expiry_date_year_not_four_digits():
    resp = client.post(
        "/todos",
        json={"expiry_date": "999-01-01", "title": "Short year expiry"},
    )
    assert resp.status_code == 400
    assert resp.json() == {"detail": "expiry_date must match format 'YYYY-MM-DD'."}

# Test Case 8: Create todo with max length title
def test_create_todo_with_max_length_title():
    max_title = "T" * 255
    resp = client.post(
        "/todos",
        json={"title": max_title},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data == {
        "id": data["id"],
        "title": max_title,
        "description": None,
        "notes": None,
        "expiry_date": None,
    }
    assert isinstance(data["id"], int)

# Test Case 9: List all todos
def test_list_all_todos():
    id1 = insert_todo("Buy groceries")
    id2 = insert_todo(
        "Submit report",
        description="Quarterly financial report",
        notes="Attach all receipts",
        expiry_date="2024-08-15",
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
            "title": "Submit report",
            "description": "Quarterly financial report",
            "notes": "Attach all receipts",
            "expiry_date": "2024-08-15",
        },
    ]
    actual = [normalize_todo(todo) for todo in todos]
    assert actual == expected

# Test Case 10: Get todo by valid id
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

# Test Case 11: Get todo by non-existent id
def test_get_todo_by_non_existent_id():
    resp = client.get("/todos/9999")
    assert resp.status_code == 404
    assert resp.json() == {"detail": "Todo not found."}

# Test Case 12: Update todo title only
def test_update_todo_title_only():
    id1 = insert_todo("Buy groceries")
    resp = client.put(f"/todos/{id1}", json={"title": "Buy fresh groceries"})
    assert resp.status_code == 200
    todo = normalize_todo(resp.json())
    expected = {
        "id": id1,
        "title": "Buy fresh groceries",
        "description": None,
        "notes": None,
        "expiry_date": None,
    }
    assert todo == expected

# Test Case 13: Update todo with all fields
def test_update_todo_with_all_fields():
    id1 = insert_todo("Buy groceries")
    resp = client.put(
        f"/todos/{id1}",
        json={
            "title": "Buy groceries",
            "description": "Weekly shopping",
            "notes": "Use coupons",
            "expiry_date": "2024-09-01",
        },
    )
    assert resp.status_code == 200
    todo = normalize_todo(resp.json())
    expected = {
        "id": id1,
        "title": "Buy groceries",
        "description": "Weekly shopping",
        "notes": "Use coupons",
        "expiry_date": "2024-09-01",
    }
    assert todo == expected

# Test Case 14: Update todo with invalid expiry_date format
def test_update_todo_with_invalid_expiry_date_format():
    id1 = insert_todo("Buy groceries")
    resp = client.put(
        f"/todos/{id1}",
        json={"expiry_date": "09-01-2024"},
    )
    assert resp.status_code == 400
    assert resp.json() == {"detail": "expiry_date must match format 'YYYY-MM-DD'."}

# Test Case 15: Update todo by non-existent id
def test_update_todo_by_non_existent_id():
    resp = client.put("/todos/9999", json={"title": "Should not exist"})
    assert resp.status_code == 404
    assert resp.json() == {"detail": "Todo not found."}

# Test Case 16: Delete todo by valid id
def test_delete_todo_by_valid_id():
    id1 = insert_todo("Buy groceries")
    resp = client.delete(f"/todos/{id1}")
    assert resp.status_code == 204
    # Confirm deleted
    resp2 = client.get(f"/todos/{id1}")
    assert resp2.status_code == 404

# Test Case 17: Delete todo by non-existent id
def test_delete_todo_by_non_existent_id():
    resp = client.delete("/todos/9999")
    assert resp.status_code == 404
    assert resp.json() == {"detail": "Todo not found."}

# Test Case 18: Create todo with description as null
def test_create_todo_with_description_as_null():
    resp = client.post(
        "/todos",
        json={"description": None, "title": "Null description"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data == {
        "id": data["id"],
        "title": "Null description",
        "description": None,
        "notes": None,
        "expiry_date": None,
    }
    assert isinstance(data["id"], int)

# Test Case 19: Create todo with notes as empty string
def test_create_todo_with_notes_as_empty_string():
    resp = client.post(
        "/todos",
        json={"notes": "", "title": "Empty notes"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data == {
        "id": data["id"],
        "title": "Empty notes",
        "description": None,
        "notes": "",
        "expiry_date": None,
    }
    assert isinstance(data["id"], int)

# Test Case 20: Create todo with expiry_date containing letters
def test_create_todo_with_expiry_date_containing_letters():
    resp = client.post(
        "/todos",
        json={"expiry_date": "2024-AB-CD", "title": "Alpha date"},
    )
    assert resp.status_code == 400
    assert resp.json() == {"detail": "expiry_date must match format 'YYYY-MM-DD'."}