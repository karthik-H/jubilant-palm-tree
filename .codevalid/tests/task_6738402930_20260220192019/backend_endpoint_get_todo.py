import pytest
from fastapi.testclient import TestClient
from backend.main import app
from unittest.mock import patch, MagicMock
from datetime import date

client = TestClient(app)

# Helper to build DB row dicts
def make_row(id, title, description=None, notes=None, expiry_date=None):
    return {
        "id": id,
        "title": title,
        "description": description,
        "notes": notes,
        "expiry_date": expiry_date,
    }

@pytest.fixture
def db_cursor_mock():
    with patch("backend.main.db_cursor") as mock_cursor_ctx:
        yield mock_cursor_ctx

# Test Case 1: Get Todo by Valid ID
def test_get_todo_by_valid_id(db_cursor_mock):
    todo_row = make_row(
        1, "Buy groceries", "Milk, eggs, bread", "Remember to check for discounts", "2024-07-15"
    )
    mock_cur = MagicMock()
    mock_cur.fetchone.return_value = todo_row
    db_cursor_mock.return_value.__enter__.return_value = mock_cur

    response = client.get("/todos/1")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Buy groceries"
    assert data["description"] == "Milk, eggs, bread"
    assert data["notes"] == "Remember to check for discounts"
    assert data["expiry_date"] == "2024-07-15"

# Test Case 2: Get Todo With Only Title
def test_get_todo_with_only_title(db_cursor_mock):
    todo_row = make_row(2, "Read book", None, None, None)
    mock_cur = MagicMock()
    mock_cur.fetchone.return_value = todo_row
    db_cursor_mock.return_value.__enter__.return_value = mock_cur

    response = client.get("/todos/2")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Read book"
    assert data["description"] is None
    assert data["notes"] is None
    assert data["expiry_date"] is None

# Test Case 3: Get Todo with Nonexistent ID
def test_get_todo_with_nonexistent_id(db_cursor_mock):
    mock_cur = MagicMock()
    mock_cur.fetchone.return_value = None
    db_cursor_mock.return_value.__enter__.return_value = mock_cur

    response = client.get("/todos/999999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Todo not found"}

# Test Case 4: Get Todo with Invalid ID Type (String)
def test_get_todo_with_invalid_id_type():
    response = client.get("/todos/abc")
    assert response.status_code == 422
    # FastAPI returns a validation error for path param type mismatch
    assert "detail" in response.json()
    assert any("value is not a valid integer" in err.get("msg", "") for err in response.json()["detail"])

# Test Case 5: Get Todo with Negative ID
def test_get_todo_with_negative_id(db_cursor_mock):
    mock_cur = MagicMock()
    mock_cur.fetchone.return_value = None
    db_cursor_mock.return_value.__enter__.return_value = mock_cur

    response = client.get("/todos/-1")
    assert response.status_code == 404
    assert response.json() == {"detail": "Todo not found"}

# Test Case 6: Get Todo with ID Zero
def test_get_todo_with_id_zero(db_cursor_mock):
    mock_cur = MagicMock()
    mock_cur.fetchone.return_value = None
    db_cursor_mock.return_value.__enter__.return_value = mock_cur

    response = client.get("/todos/0")
    assert response.status_code == 404
    assert response.json() == {"detail": "Todo not found"}

# Test Case 7: Get Todo with Large Integer ID
def test_get_todo_with_large_integer_id(db_cursor_mock):
    mock_cur = MagicMock()
    mock_cur.fetchone.return_value = None
    db_cursor_mock.return_value.__enter__.return_value = mock_cur

    response = client.get("/todos/9223372036854775807")
    assert response.status_code == 404
    assert response.json() == {"detail": "Todo not found"}

# Test Case 8: Get Todo After Deletion
def test_get_todo_after_deletion(db_cursor_mock):
    mock_cur = MagicMock()
    mock_cur.fetchone.return_value = None
    db_cursor_mock.return_value.__enter__.return_value = mock_cur

    response = client.get("/todos/3")
    assert response.status_code == 404
    assert response.json() == {"detail": "Todo not found"}

# Test Case 9: Get Todo with Null Expiry Date
def test_get_todo_with_null_expiry_date(db_cursor_mock):
    todo_row = make_row(
        4, "Call mom", "Weekly check-in", None, None
    )
    mock_cur = MagicMock()
    mock_cur.fetchone.return_value = todo_row
    db_cursor_mock.return_value.__enter__.return_value = mock_cur

    response = client.get("/todos/4")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Call mom"
    assert data["description"] == "Weekly check-in"
    assert data["notes"] is None
    assert data["expiry_date"] is None

# Test Case 10: Get Todo With Optional Fields Absent
def test_get_todo_with_optional_fields_absent(db_cursor_mock):
    todo_row = make_row(5, "Finish project", None, None, None)
    mock_cur = MagicMock()
    mock_cur.fetchone.return_value = todo_row
    db_cursor_mock.return_value.__enter__.return_value = mock_cur

    response = client.get("/todos/5")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Finish project"
    assert data["description"] is None
    assert data["notes"] is None
    assert data["expiry_date"] is None