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

# Test Case 1: Get Todo By ID - Success With All Fields
def test_get_todo_by_id_success_all_fields(db_cursor_mock):
    todo_row = make_row(
        1, "Test Todo", "This is a test todo.", "Some notes here.", "2024-12-31"
    )
    mock_cur = MagicMock()
    mock_cur.fetchone.return_value = todo_row
    db_cursor_mock.return_value.__enter__.return_value = mock_cur

    response = client.get("/todos/1")
    assert response.status_code == 200
    assert response.json() == {
        "title": "Test Todo",
        "description": "This is a test todo.",
        "notes": "Some notes here.",
        "expiry_date": "2024-12-31"
    }

# Test Case 2: Get Todo By ID - Only Required Field Present
def test_get_todo_by_id_only_required_field(db_cursor_mock):
    todo_row = make_row(2, "Title Only Todo", None, None, None)
    mock_cur = MagicMock()
    mock_cur.fetchone.return_value = todo_row
    db_cursor_mock.return_value.__enter__.return_value = mock_cur

    response = client.get("/todos/2")
    assert response.status_code == 200
    assert response.json() == {
        "title": "Title Only Todo",
        "description": None,
        "notes": None,
        "expiry_date": None
    }

# Test Case 3: Get Todo By ID - Not Found
def test_get_todo_by_id_not_found(db_cursor_mock):
    mock_cur = MagicMock()
    mock_cur.fetchone.return_value = None
    db_cursor_mock.return_value.__enter__.return_value = mock_cur

    response = client.get("/todos/99999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Todo not found"}

# Test Case 4: Get Todo By ID - Invalid Non-integer ID
def test_get_todo_by_id_invalid_non_integer_id():
    response = client.get("/todos/abc")
    # Accept either 422 or 400, per spec
    assert response.status_code in (400, 422)
    # Accept either FastAPI validation or custom error
    resp = response.json()
    if response.status_code == 422:
        assert "detail" in resp
        # FastAPI validation error
        assert any("value is not a valid integer" in err.get("msg", "") for err in resp["detail"])
    else:
        assert resp == {"detail": "Invalid todo id"}

# Test Case 5: Get Todo By ID - Edge Case: ID Zero
def test_get_todo_by_id_edge_case_id_zero(db_cursor_mock):
    mock_cur = MagicMock()
    mock_cur.fetchone.return_value = None
    db_cursor_mock.return_value.__enter__.return_value = mock_cur

    response = client.get("/todos/0")
    assert response.status_code == 404
    assert response.json() == {"detail": "Todo not found"}

# Test Case 6: Get Todo By ID - Edge Case: Very Large ID
def test_get_todo_by_id_edge_case_very_large_id(db_cursor_mock):
    mock_cur = MagicMock()
    mock_cur.fetchone.return_value = None
    db_cursor_mock.return_value.__enter__.return_value = mock_cur

    response = client.get("/todos/999999999999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Todo not found"}

# Test Case 7: Get Todo By ID - Optional Fields Are Null
def test_get_todo_by_id_optional_fields_null(db_cursor_mock):
    todo_row = make_row(3, "Null Optionals Todo", None, None, None)
    mock_cur = MagicMock()
    mock_cur.fetchone.return_value = todo_row
    db_cursor_mock.return_value.__enter__.return_value = mock_cur

    response = client.get("/todos/3")
    assert response.status_code == 200
    assert response.json() == {
        "title": "Null Optionals Todo",
        "description": None,
        "notes": None,
        "expiry_date": None
    }

# Test Case 8: Get Todo By ID - Past Expiry Date
def test_get_todo_by_id_past_expiry_date(db_cursor_mock):
    todo_row = make_row(4, "Past Expiry", "This todo has a past expiry date.", None, "2000-01-01")
    mock_cur = MagicMock()
    mock_cur.fetchone.return_value = todo_row
    db_cursor_mock.return_value.__enter__.return_value = mock_cur

    response = client.get("/todos/4")
    assert response.status_code == 200
    assert response.json() == {
        "title": "Past Expiry",
        "description": "This todo has a past expiry date.",
        "notes": None,
        "expiry_date": "2000-01-01"
    }

# Test Case 9: Get Todo By ID - Long Text Fields
def test_get_todo_by_id_long_text_fields(db_cursor_mock):
    long_title = "T" * 255
    long_description = "D" * 1024
    long_notes = "N" * 1024
    todo_row = make_row(5, long_title, long_description, long_notes, "2025-05-31")
    mock_cur = MagicMock()
    mock_cur.fetchone.return_value = todo_row
    db_cursor_mock.return_value.__enter__.return_value = mock_cur

    response = client.get("/todos/5")
    assert response.status_code == 200
    assert response.json() == {
        "title": long_title,
        "description": long_description,
        "notes": long_notes,
        "expiry_date": "2025-05-31"
    }

# Test Case 10: Get Todo By ID - Database Row Missing Optional Fields
def test_get_todo_by_id_db_row_missing_optionals(db_cursor_mock):
    # Simulate legacy DB row with only title present
    todo_row = {"id": 6, "title": "Legacy Todo"}
    mock_cur = MagicMock()
    mock_cur.fetchone.return_value = todo_row
    db_cursor_mock.return_value.__enter__.return_value = mock_cur

    response = client.get("/todos/6")
    assert response.status_code == 200
    assert response.json() == {
        "title": "Legacy Todo",
        "description": None,
        "notes": None,
        "expiry_date": None
    }