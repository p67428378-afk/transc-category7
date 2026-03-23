from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import pytest

from backend.main import app, get_db
from backend.database import Base

# Use an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(name="db_session")
def db_session_fixture():
    # Create the database tables
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Drop all tables after the test
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(name="client")
def client_fixture(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

def test_create_user(client):
    response = client.post(
        "/users/",
        json={"name": "Test User", "email": "test_create@example.com"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test_create@example.com"
    assert "id" in data

def test_create_user_duplicate_email(client):
    # Create user first
    client.post(
        "/users/",
        json={"name": "Test User", "email": "test_duplicate@example.com"},
    )
    # Try to create with duplicate email
    response = client.post(
        "/users/",
        json={"name": "Test User 2", "email": "test_duplicate@example.com"},
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Email already registered"}

def test_read_users(client):
    client.post(
        "/users/",
        json={"name": "Test User 3", "email": "test_read_users@example.com"},
    )
    response = client.get("/users/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0

def test_read_user(client):
    create_response = client.post(
        "/users/",
        json={"name": "Test User 4", "email": "test_read_user@example.com"},
    )
    user_id = create_response.json()["id"]
    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test_read_user@example.com"

def test_read_nonexistent_user(client):
    response = client.get("/users/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}

def test_upload_transactions_csv(client):
    with open("test.csv", "w") as f:
        f.write("date,description,amount\n")
        f.write("2023-01-01,Coffee,5.50\n")
        f.write("2023-01-02,Groceries,50.00\n")

    with open("test.csv", "rb") as f:
        response = client.post(
            "/api/transactions/upload",
            files={
                "file": ("test.csv", f, "text/csv")
            }
        )
    assert response.status_code == 200
    response_data = response.json()
    expected_path = os.path.normpath(os.path.join("./uploads", "test.csv"))
    assert response_data["message"] == "File uploaded successfully"
    assert response_data["filename"] == "test.csv"
    assert os.path.normpath(response_data["path"]) == expected_path

    # Clean up the test file
    os.remove("test.csv")
    os.remove(expected_path)

def test_upload_transactions_non_csv(client):
    with open("test.txt", "w") as f:
        f.write("not a csv")

    with open("test.txt", "rb") as f:
        response = client.post(
            "/api/transactions/upload",
            files={
                "file": ("test.txt", f, "text/plain")
            }
        )
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid file format. Only CSV files are allowed."}

    # Clean up the test file
    os.remove("test.txt")
