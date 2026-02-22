import pytest
from fastapi.testclient import TestClient
from backend.main import app
from unittest.mock import patch, MagicMock

client = TestClient(app)

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

# Test Case 1: Get Existing Todo by Valid ID
def test_get_existing_todo_by_valid_id(db_cursor_mock):
    todo_row = make_row(
        1, "Buy groceries", "Milk, eggs, bread", "Remember to check discounts", "2024-07-01"
    )
    mock_cur = MagicMock()
    mock_cur.fetchone.return_value = todo_row
    db_cursor_mock.return_value.__enter__.return_value = mock_cur

    response = client.get("/todos/1")
    assert response.status_code == 200
    assert response.json() == {
        "description": "Milk, eggs, bread",
        "expiry_date": "2024-07-01",
        "notes": "Remember to check discounts",
        "title": "Buy groceries"
    }

# Test Case 2: Get Todo with Optional Fields Null
def test_get_todo_with_optional_fields_null(db_cursor_mock):
    todo_row = make_row(2, "Read book", None, None, None)
    mock_cur = MagicMock()
    mock_cur.fetchone.return_value = todo_row
    db_cursor_mock.return_value.__enter__.return_value = mock_cur

    response = client.get("/todos/2")
    assert response.status_code == 200
    assert response.json() == {
        "description": None,
        "expiry_date": None,
        "notes": None,
        "title": "Read book"
    }

# Test Case 3: Get Todo with Nonexistent ID
def test_get_todo_with_nonexistent_id(db_cursor_mock):
    mock_cur = MagicMock()
    mock_cur.fetchone.return_value = None
    db_cursor_mock.return_value.__enter__.return_value = mock_cur

    response = client.get("/todos/99999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Todo not found"}

# Test Case 4: Get Todo with Invalid ID Format
def test_get_todo_with_invalid_id_format():
    response = client.get("/todos/abc")
    assert response.status_code == 422
    # FastAPI returns a validation error for path param type mismatch
    assert "detail" in response.json()
    # Accept either default FastAPI error or custom error
    assert any("value is not a valid integer" in err.get("msg", "") for err in response.json()["detail"]) or response.json() == {"detail": "Invalid ID format"}

# Test Case 5: Get Todo with Minimum Possible ID
def test_get_todo_with_minimum_possible_id(db_cursor_mock):
    todo_row = make_row(
        1, "Buy groceries", "Milk, eggs, bread", "Remember to check discounts", "2024-07-01"
    )
    mock_cur = MagicMock()
    mock_cur.fetchone.return_value = todo_row
    db_cursor_mock.return_value.__enter__.return_value = mock_cur

    response = client.get("/todos/1")
    assert response.status_code == 200
    assert response.json() == {
        "description": "Milk, eggs, bread",
        "expiry_date": "2024-07-01",
        "notes": "Remember to check discounts",
        "title": "Buy groceries"
    }

# Test Case 6: Get Todo with Maximum Integer ID
def test_get_todo_with_maximum_integer_id(db_cursor_mock):
    mock_cur = MagicMock()
    mock_cur.fetchone.return_value = None
    db_cursor_mock.return_value.__enter__.return_value = mock_cur

    response = client.get("/todos/2147483647")
    assert response.status_code == 404
    assert response.json() == {"detail": "Todo not found"}

# Test Case 7: Get Todo with ID Zero
def test_get_todo_with_id_zero(db_cursor_mock):
    mock_cur = MagicMock()
    mock_cur.fetchone.return_value = None
    db_cursor_mock.return_value.__enter__.return_value = mock_cur

    response = client.get("/todos/0")
    assert response.status_code == 404
    assert response.json() == {"detail": "Todo not found"}

# Test Case 8: Get Todo with Negative ID
def test_get_todo_with_negative_id(db_cursor_mock):
    mock_cur = MagicMock()
    mock_cur.fetchone.return_value = None
    db_cursor_mock.return_value.__enter__.return_value = mock_cur

    response = client.get("/todos/-1")
    assert response.status_code == 404
    assert response.json() == {"detail": "Todo not found"}

# Test Case 9: Get Todo with Only Required Field
def test_get_todo_with_only_required_field(db_cursor_mock):
    todo_row = make_row(3, "Finish assignment", None, None, None)
    mock_cur = MagicMock()
    mock_cur.fetchone.return_value = todo_row
    db_cursor_mock.return_value.__enter__.return_value = mock_cur

    response = client.get("/todos/3")
    assert response.status_code == 200
    assert response.json() == {
        "description": None,
        "expiry_date": None,
        "notes": None,
        "title": "Finish assignment"
    }

# Test Case 10: Get Todo with Expiry Date Edge Case
def test_get_todo_with_expiry_date_edge_case(db_cursor_mock):
    todo_row = make_row(4, "Check server backup", "Oldest record", "", "1900-01-01")
    mock_cur = MagicMock()
    mock_cur.fetchone.return_value = todo_row
    db_cursor_mock.return_value.__enter__.return_value = mock_cur

    response = client.get("/todos/4")
    assert response.status_code == 200
    assert response.json() == {
        "description": "Oldest record",
        "expiry_date": "1900-01-01",
        "notes": "",
        "title": "Check server backup"
    }