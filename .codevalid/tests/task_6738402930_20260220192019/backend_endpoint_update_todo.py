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

def setup_todo(client, todo_id=1, title="Existing Title", description="Existing description", notes="Existing notes", expiry_date="2025-01-01"):
    # Create or update a todo for test setup
    client.post("/todos", json={
        "id": todo_id,
        "title": title,
        "description": description,
        "notes": notes,
        "expiry_date": expiry_date
    })

# Test Case 1: Update existing todo with all fields
def test_update_existing_todo_all_fields(client):
    setup_todo(client)
    response = client.put("/todos/1", json={
        "description": "Updated description",
        "expiry_date": "2030-12-31",
        "notes": "Updated notes",
        "title": "Updated Title"
    })
    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "description": "Updated description",
        "expiry_date": "2030-12-31",
        "notes": "Updated notes",
        "title": "Updated Title"
    }

# Test Case 2: Update existing todo with only description field
def test_update_existing_todo_only_description(client):
    setup_todo(client, description="Old description")
    response = client.put("/todos/1", json={
        "description": "New partial description"
    })
    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "description": "New partial description",
        "expiry_date": "2025-01-01",
        "notes": "Existing notes",
        "title": "Existing Title"
    }

# Test Case 3: Update todo with empty body (no fields)
def test_update_todo_empty_body(client):
    setup_todo(client)
    response = client.put("/todos/1", json={})
    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "description": "Existing description",
        "expiry_date": "2025-01-01",
        "notes": "Existing notes",
        "title": "Existing Title"
    }

# Test Case 4: Reject update with empty title
def test_reject_update_empty_title(client):
    setup_todo(client)
    response = client.put("/todos/1", json={"title": ""})
    assert response.status_code == 400
    assert response.json() == {"error": "Title must not be empty"}

# Test Case 5: Reject update with invalid expiry_date format
def test_reject_update_invalid_expiry_date_format(client):
    setup_todo(client)
    response = client.put("/todos/1", json={"expiry_date": "12-31-2030"})
    assert response.status_code == 400
    assert response.json() == {"error": "expiry_date must be in 'YYYY-MM-DD' format"}

# Test Case 6: Reject update with non-string expiry_date
def test_reject_update_non_string_expiry_date(client):
    setup_todo(client)
    response = client.put("/todos/1", json={"expiry_date": 20221231})
    assert response.status_code == 400
    assert response.json() == {"error": "expiry_date must be a string in 'YYYY-MM-DD' format"}

# Test Case 7: Update non-existent todo
def test_update_non_existent_todo(client):
    response = client.put("/todos/9999", json={"title": "Should Not Exist"})
    assert response.status_code == 404
    assert response.json() == {"error": "Todo not found"}

# Test Case 8: Update todo with maximum length title
def test_update_todo_max_length_title(client):
    setup_todo(client)
    long_title = "T" * 255
    response = client.put("/todos/1", json={"title": long_title})
    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "description": "Existing description",
        "expiry_date": "2025-01-01",
        "notes": "Existing notes",
        "title": long_title
    }

# Test Case 9: Reject update with whitespace-only title
def test_reject_update_whitespace_only_title(client):
    setup_todo(client)
    response = client.put("/todos/1", json={"title": "    "})
    assert response.status_code == 400
    assert response.json() == {"error": "Title must not be empty"}

# Test Case 10: Update todo with earliest valid expiry_date
def test_update_todo_earliest_expiry_date(client):
    setup_todo(client)
    response = client.put("/todos/1", json={"expiry_date": "0001-01-01"})
    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "description": "Existing description",
        "expiry_date": "0001-01-01",
        "notes": "Existing notes",
        "title": "Existing Title"
    }

# Test Case 11: Update todo with far-future expiry_date
def test_update_todo_far_future_expiry_date(client):
    setup_todo(client)
    response = client.put("/todos/1", json={"expiry_date": "9999-12-31"})
    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "description": "Existing description",
        "expiry_date": "9999-12-31",
        "notes": "Existing notes",
        "title": "Existing Title"
    }

# Test Case 12: Update todo setting description to null
def test_update_todo_description_to_null(client):
    setup_todo(client, description="Non-null description")
    response = client.put("/todos/1", json={"description": None})
    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "description": None,
        "expiry_date": "2025-01-01",
        "notes": "Existing notes",
        "title": "Existing Title"
    }

# Test Case 13: Update todo setting notes to null
def test_update_todo_notes_to_null(client):
    setup_todo(client, notes="Non-null notes")
    response = client.put("/todos/1", json={"notes": None})
    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "description": "Existing description",
        "expiry_date": "2025-01-01",
        "notes": None,
        "title": "Existing Title"
    }

# Test Case 14: Update todo setting expiry_date to null
def test_update_todo_expiry_date_to_null(client):
    setup_todo(client, expiry_date="2025-01-01")
    response = client.put("/todos/1", json={"expiry_date": None})
    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "description": "Existing description",
        "expiry_date": None,
        "notes": "Existing notes",
        "title": "Existing Title"
    }

# Test Case 15: Reject update with invalid JSON body
def test_reject_update_invalid_json_body(client):
    setup_todo(client)
    # Send malformed JSON
    response = client.put("/todos/1", data='{ "title": "Missing quote }', headers={"Content-Type": "application/json"})
    assert response.status_code == 400
    assert response.json() == {"error": "Malformed JSON"}