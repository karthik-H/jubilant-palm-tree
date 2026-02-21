import pytest
from fastapi.testclient import TestClient
from backend.main import app
import backend.database as db
import os
import shutil
import tempfile

@pytest.fixture(scope="function")
def test_db():
    # Setup: copy the original DB to a temp location for isolation
    orig_db_path = os.path.join(os.path.dirname(__file__), "../../backend/todos.db")
    temp_dir = tempfile.mkdtemp()
    temp_db_path = os.path.join(temp_dir, "test_todos.db")
    shutil.copy(orig_db_path, temp_db_path)
    db.DATABASE_PATH = temp_db_path
    yield
    # Teardown: remove temp db
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

# Test Case 1: Update all fields with valid values
def test_update_all_fields_valid(client):
    setup_todo(client, 1, "Original Title", "Original Description", "Original Notes", "2024-01-01")
    response = client.put("/todos/1", json={
        "description": "Updated Description",
        "expiry_date": "2024-12-31",
        "notes": "Updated Notes",
        "title": "Updated Title"
    })
    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "description": "Updated Description",
        "expiry_date": "2024-12-31",
        "notes": "Updated Notes",
        "title": "Updated Title"
    }

# Test Case 2: Partial update - only description
def test_partial_update_description(client):
    setup_todo(client, 2, "Sample Title 2", "Original Description", "Original Notes", "2024-10-10")
    response = client.put("/todos/2", json={
        "description": "New Partial Description"
    })
    assert response.status_code == 200
    assert response.json() == {
        "id": 2,
        "description": "New Partial Description",
        "expiry_date": "2024-10-10",
        "notes": "Original Notes",
        "title": "Sample Title 2"
    }

# Test Case 3: Attempt to update title to an empty string
def test_update_title_empty_string(client):
    setup_todo(client, 3, "Title 3", "Desc 3", "Notes 3", "2024-11-11")
    response = client.put("/todos/3", json={"title": ""})
    assert response.status_code == 400
    assert response.json() == {"detail": "Title cannot be empty"}

# Test Case 4: Attempt to update expiry_date with invalid format
def test_update_expiry_date_invalid_format(client):
    setup_todo(client, 4, "Title 4", "Desc 4", "Notes 4", "2024-12-12")
    response = client.put("/todos/4", json={"expiry_date": "31-12-2024"})
    assert response.status_code == 400
    assert response.json() == {"detail": "expiry_date must be in 'YYYY-MM-DD' format"}

# Test Case 5: Update non-existent todo
def test_update_non_existent_todo(client):
    response = client.put("/todos/99999", json={"title": "Should Not Exist"})
    assert response.status_code == 404
    assert response.json() == {"detail": "Todo not found"}

# Test Case 6: No fields provided for update
def test_update_no_fields_provided(client):
    setup_todo(client, 5, "Title 5", "Description 5", "Notes 5", "2024-05-05")
    response = client.put("/todos/5", json={})
    assert response.status_code == 400
    assert response.json() == {"detail": "At least one field must be provided for update"}

# Test Case 7: Update notes to null
def test_update_notes_to_null(client):
    setup_todo(client, 6, "Title 6", "Description 6", "Notes 6", None)
    response = client.put("/todos/6", json={"notes": None})
    assert response.status_code == 200
    assert response.json() == {
        "id": 6,
        "description": "Description 6",
        "expiry_date": None,
        "notes": None,
        "title": "Title 6"
    }

# Test Case 8: Update title to maximum allowed length
def test_update_title_max_length(client):
    setup_todo(client, 7, "Title 7", "Desc 7", "Notes 7", "2025-01-01")
    max_title = "T" * 255
    response = client.put("/todos/7", json={"title": max_title})
    assert response.status_code == 200
    assert response.json() == {
        "id": 7,
        "description": "Desc 7",
        "expiry_date": "2025-01-01",
        "notes": "Notes 7",
        "title": max_title
    }

# Test Case 9: Remove expiry_date (set to null)
def test_remove_expiry_date(client):
    setup_todo(client, 8, "Title 8", "Description 8", "Notes 8", "2024-06-06")
    response = client.put("/todos/8", json={"expiry_date": None})
    assert response.status_code == 200
    assert response.json() == {
        "id": 8,
        "description": "Description 8",
        "expiry_date": None,
        "notes": "Notes 8",
        "title": "Title 8"
    }

# Test Case 10: Update with extra unexpected field
def test_update_with_extra_field(client):
    setup_todo(client, 9, "Title 9", "Description 9", "Notes 9", None)
    response = client.put("/todos/9", json={
        "description": "Updated description for 9",
        "unexpected_field": "should be ignored"
    })
    assert response.status_code == 200
    assert response.json() == {
        "id": 9,
        "description": "Updated description for 9",
        "expiry_date": None,
        "notes": "Notes 9",
        "title": "Title 9"
    }

# Test Case 11: Update expiry_date to valid leap year date
def test_update_expiry_date_leap_year(client):
    setup_todo(client, 10, "Title 10", "Description 10", "Notes 10", "2023-01-01")
    response = client.put("/todos/10", json={"expiry_date": "2024-02-29"})
    assert response.status_code == 200
    assert response.json() == {
        "id": 10,
        "description": "Description 10",
        "expiry_date": "2024-02-29",
        "notes": "Notes 10",
        "title": "Title 10"
    }

# Test Case 12: Update all fields to empty strings (except expiry_date)
def test_update_all_fields_empty_strings(client):
    setup_todo(client, 11, "Title 11", "Description 11", "Notes 11", "2024-11-11")
    response = client.put("/todos/11", json={
        "description": "",
        "expiry_date": "",
        "notes": "",
        "title": ""
    })
    assert response.status_code == 400
    assert response.json() == {"detail": "Title cannot be empty; expiry_date must be in 'YYYY-MM-DD' format"}