import pytest
from fastapi.testclient import TestClient
from backend.main import app
import backend.database as db
import os
import shutil
import tempfile

@pytest.fixture(scope="function")
def test_db():
    orig_db_path = os.path.join(os.path.dirname(__file__), "../../backend/todos.db")
    temp_dir = tempfile.mkdtemp()
    temp_db_path = os.path.join(temp_dir, "test_todos.db")
    shutil.copy(orig_db_path, temp_db_path)
    db.DATABASE_PATH = temp_db_path
    yield
    shutil.rmtree(temp_dir)
    db.DATABASE_PATH = orig_db_path

@pytest.fixture(scope="function")
def client(test_db):
    return TestClient(app)

def setup_todo(client, todo_id, title, description, notes, expiry_date):
    client.post("/todos", json={
        "id": todo_id,
        "title": title,
        "description": description,
        "notes": notes,
        "expiry_date": expiry_date
    })

# Test Case 1: Update all fields of an existing todo
def test_update_all_fields_existing_todo(client):
    setup_todo(client, 1, "Original Title", "Original Description", "Original Notes", "2025-05-30")
    response = client.put("/todos/1", json={
        "description": "Updated Description",
        "expiry_date": "2025-05-30",
        "notes": "Updated Notes",
        "title": "Updated Title"
    })
    assert response.status_code == 200
    assert response.json() == {
        "description": "Updated Description",
        "expiry_date": "2025-05-30",
        "notes": "Updated Notes",
        "title": "Updated Title"
    }

# Test Case 2: Update partial fields of an existing todo
def test_update_partial_fields_existing_todo(client):
    setup_todo(client, 2, "Original", "Original Description", "Original Notes", "2026-01-01")
    response = client.put("/todos/2", json={
        "notes": "Partial update notes",
        "title": "Partially Updated Title"
    })
    assert response.status_code == 200
    assert response.json() == {
        "description": "Original Description",
        "expiry_date": "2026-01-01",
        "notes": "Partial update notes",
        "title": "Partially Updated Title"
    }

# Test Case 3: Update with no fields (empty object)
def test_update_with_no_fields_empty_object(client):
    setup_todo(client, 3, "Original Title", "Original Description", None, None)
    response = client.put("/todos/3", json={})
    assert response.status_code == 200
    assert response.json() == {
        "description": "Original Description",
        "expiry_date": None,
        "notes": None,
        "title": "Original Title"
    }

# Test Case 4: Update a non-existent todo
def test_update_non_existent_todo(client):
    response = client.put("/todos/9999", json={"title": "Should not work"})
    assert response.status_code == 404
    assert response.json() == {"detail": "Todo not found"}

# Test Case 5: Update with invalid expiry_date format
def test_update_invalid_expiry_date_format(client):
    setup_todo(client, 4, "Valid Title", "Valid Description", None, None)
    response = client.put("/todos/4", json={"expiry_date": "30-12-2025"})
    assert response.status_code == 400
    assert response.json() == {"detail": "expiry_date must be in 'YYYY-MM-DD' format"}

# Test Case 6: Update title to empty string
def test_update_title_to_empty_string(client):
    setup_todo(client, 5, "Valid Title", "Valid Description", None, None)
    response = client.put("/todos/5", json={"title": ""})
    assert response.status_code == 400
    assert response.json() == {"detail": "Title must not be empty"}

# Test Case 7: Update to remove expiry_date
def test_update_remove_expiry_date(client):
    setup_todo(client, 6, "Todo with expiry", "Original Desc", None, "2027-09-28")
    response = client.put("/todos/6", json={"expiry_date": None})
    assert response.status_code == 200
    assert response.json() == {
        "description": "Original Desc",
        "expiry_date": None,
        "notes": None,
        "title": "Todo with expiry"
    }

# Test Case 8: Update title to maximum allowed length
def test_update_title_max_length(client):
    setup_todo(client, 7, "Desc", "Desc", None, None)
    max_title = "T" * 255
    response = client.put("/todos/7", json={"title": max_title})
    assert response.status_code == 200
    assert response.json() == {
        "description": "Desc",
        "expiry_date": None,
        "notes": None,
        "title": max_title
    }

# Test Case 9: Update expiry_date to a past date
def test_update_expiry_date_past(client):
    setup_todo(client, 8, "Old Expiry", "Past expiry", None, None)
    response = client.put("/todos/8", json={"expiry_date": "2000-01-01"})
    assert response.status_code == 200
    assert response.json() == {
        "description": "Past expiry",
        "expiry_date": "2000-01-01",
        "notes": None,
        "title": "Old Expiry"
    }

# Test Case 10: Update with title omitted
def test_update_description_only(client):
    setup_todo(client, 9, "Existing Title", "Should change", "Some notes", None)
    response = client.put("/todos/9", json={"description": "Updated only description"})
    assert response.status_code == 200
    assert response.json() == {
        "description": "Updated only description",
        "expiry_date": None,
        "notes": "Some notes",
        "title": "Existing Title"
    }

# Test Case 11: Update notes to empty string
def test_update_notes_to_empty_string(client):
    setup_todo(client, 10, "Todo 10", "Notes cleared", "Some note", None)
    response = client.put("/todos/10", json={"notes": ""})
    assert response.status_code == 200
    assert response.json() == {
        "description": "Notes cleared",
        "expiry_date": None,
        "notes": "",
        "title": "Todo 10"
    }

# Test Case 12: Update expiry_date with time component
def test_update_expiry_date_with_time_component(client):
    setup_todo(client, 11, "Valid Title", "Valid Description", None, None)
    response = client.put("/todos/11", json={"expiry_date": "2024-12-31T23:59:59"})
    assert response.status_code == 400
    assert response.json() == {"detail": "expiry_date must be in 'YYYY-MM-DD' format"}