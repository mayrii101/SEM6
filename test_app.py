import pytest
from unittest.mock import MagicMock, patch

from festival_api import app   # ✅ FIXED IMPORT


# =========================================
# HAPPY FLOW
# =========================================

@pytest.fixture
def client():
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client


# running api


def test_home(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.get_json() == {
        "message": "Festival API Running"
    }


# GET /zones


@patch("festival_api.mysql.connector.connect")
def test_get_zones(mock_connect, client):
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [
        {"ID": 1, "Name": "Main Stage", "Color": "Green"}
    ]

    mock_db = MagicMock()
    mock_db.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_db

    response = client.get("/zones")

    assert response.status_code == 200
    assert response.get_json() == [
        {"ID": 1, "Name": "Main Stage", "Color": "Green"}
    ]


# GET /zone-status


@patch("festival_api.mysql.connector.connect")
def test_zone_status(mock_connect, client):
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [
        {
            "Name": "Main Stage",
            "Color": "Green",
            "CurrentCount": 100,
            "DensityLevel": "Low",
            "UpdatedAt": "2025-01-01 12:00:00"
        }
    ]

    mock_db = MagicMock()
    mock_db.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_db

    response = client.get("/zone-status")

    assert response.status_code == 200
    data = response.get_json()

    assert data[0]["Name"] == "Main Stage"
    assert data[0]["CurrentCount"] == 100


# POST /user


@patch("festival_api.mysql.connector.connect")
def test_create_user(mock_connect, client):
    mock_cursor = MagicMock()

    mock_db = MagicMock()
    mock_db.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_db

    payload = {
        "name": "John Doe",
        "dob": "2000-01-01",
        "gender": "Male",
        "phone": "0612345678"
    }

    response = client.post("/users", json=payload)

    assert response.status_code == 200
    assert response.get_json() == {"status": "success"}

    mock_cursor.execute.assert_called_once()
    mock_db.commit.assert_called_once()


# POST /distress


@patch("festival_api.mysql.connector.connect")
def test_send_distress(mock_connect, client):
    mock_cursor = MagicMock()

    mock_db = MagicMock()
    mock_db.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_db

    payload = {
        "message": "Help needed",
        "zone_id": 2,
        "user_id": 5
    }

    response = client.post("/distress", json=payload)

    assert response.status_code == 200
    assert response.get_json() == {"status": "alert received"}

    mock_cursor.execute.assert_called_once()
    mock_db.commit.assert_called_once()


# GET /distress


@patch("festival_api.mysql.connector.connect")
def test_get_distress(mock_connect, client):
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [
        {
            "ID": 1,
            "Message": "Need help",
            "Sender": "John",
            "Zone": "Main Stage"
        }
    ]

    mock_db = MagicMock()
    mock_db.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_db

    response = client.get("/distress")

    assert response.status_code == 200
    data = response.get_json()

    assert data[0]["Message"] == "Need help"


# GET /people


@patch("festival_api.mysql.connector.connect")
def test_get_people(mock_connect, client):
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [
        {"ZoneID": 1, "CurrentCount": 500}
    ]

    mock_db = MagicMock()
    mock_db.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_db

    response = client.get("/people")

    assert response.status_code == 200
    assert response.get_json() == [
        {"ZoneID": 1, "CurrentCount": 500}
    ]

# =========================================
# EDGE CASE
# ========================================

# missing fields user post


def test_create_user_missing_fields(client):
    response = client.post("/users", json={
        "name": "John Doe"
        # missing dob, gender, phone
    })

    assert response.status_code == 400

# missing full json user post


def test_create_user_no_json(client):
    response = client.post("/users")

    assert response.status_code in [400, 500]

# missing fields distress message post


def test_distress_missing_fields(client):
    response = client.post("/distress", json={
        "message": "Help"
        # missing zone_id, user_id
    })

    assert response.status_code == 400

# empty zone table


@patch("festival_api.mysql.connector.connect")
def test_get_zones_empty(mock_connect, client):
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = []

    mock_db = MagicMock()
    mock_db.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_db

    response = client.get("/zones")

    assert response.status_code == 200
    assert response.get_json() == []

# empty distress message get


@patch("festival_api.mysql.connector.connect")
def test_get_distress_empty(mock_connect, client):
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = []

    mock_db = MagicMock()
    mock_db.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_db

    response = client.get("/distress")

    assert response.status_code == 200
    assert response.get_json() == []


# database fail
@patch("festival_api.mysql.connector.connect")
def test_db_connection_failure(mock_connect, client):
    mock_connect.side_effect = Exception("DB down")

    response = client.get("/zones")

    assert response.status_code == 400

# SQL fail


@patch("festival_api.mysql.connector.connect")
def test_sql_failure(mock_connect, client):
    mock_db = MagicMock()
    mock_db.cursor.side_effect = Exception("SQL error")
    mock_connect.return_value = mock_db

    response = client.get("/people")

    assert response.status_code == 400

# =========================================
# EDGE CASE PT 2
# ========================================


def test_malformed_json_users(client):
    response = client.post(
        "/users",
        data="{bad json",
        content_type="application/json"
    )

    assert response.status_code == 400

# verkeerd data type


def test_create_user_wrong_types(client):
    response = client.post("/users", json={
        "name": 123,
        "dob": True,
        "gender": [],
        "phone": {}
    })

    assert response.status_code == 400

# sql injection security test


def test_sql_injection_attempt(client):
    response = client.post("/users", json={
        "name": "Robert'); DROP TABLE Users;--",
        "dob": "2000-01-01",
        "gender": "Male",
        "phone": "0612345678"
    })

    # should still be safely rejected or handled
    assert response.status_code in [200, 400]

# extreme payload


def test_large_payload(client):
    response = client.post("/users", json={
        "name": "x" * 10000,
        "dob": "2000-01-01",
        "gender": "Male",
        "phone": "0" * 5000
    })

    assert response.status_code == 400

# verkeerde db structure


@patch("festival_api.mysql.connector.connect")
def test_db_returns_invalid_shape(mock_connect, client):
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [{}]  # foute row

    mock_db = MagicMock()
    mock_db.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_db

    response = client.get("/zones")

    assert response.status_code == 200

# null fields van db


@patch("festival_api.mysql.connector.connect")
def test_db_returns_null_values(mock_connect, client):
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [
        {"ID": None, "Name": None, "Color": None}
    ]

    mock_db = MagicMock()
    mock_db.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_db

    response = client.get("/zones")

    assert response.status_code == 200

# wrong HTTP


def test_wrong_method_users(client):
    response = client.get("/users")

    assert response.status_code == 405

# lege values


def test_empty_string_user(client):
    response = client.post("/users", json={
        "name": "",
        "dob": "",
        "gender": "",
        "phone": ""
    })

    assert response.status_code == 400

# no content header


def test_missing_content_type(client):
    response = client.post("/users", data='{"name":"John"}')

    assert response.status_code == 400

# return broken db


@patch("festival_api.mysql.connector.connect")
def test_distress_broken_db_row(mock_connect, client):
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [
        {"ID": 1},  # geen fields
    ]

    mock_db = MagicMock()
    mock_db.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_db

    response = client.get("/distress")

    assert response.status_code == 200
