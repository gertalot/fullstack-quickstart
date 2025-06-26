import os
import pathlib
import pytest
from fastapi.testclient import TestClient
from app import my_app
from app.db import get_engine, Base

os.environ["GOOGLE_CLIENT_ID"] = "dummy-client-id"
os.environ["GOOGLE_CLIENT_SECRET"] = "dummy-client-secret"
os.environ["JWT_SECRET"] = "dummy-jwt-secret"
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

TEST_DB_PATH = pathlib.Path("./test.db")

@pytest.fixture(scope="session", autouse=True)
def create_all_tables(request):
    engine = get_engine()
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    def cleanup():
        if TEST_DB_PATH.exists():
            TEST_DB_PATH.unlink()
    request.addfinalizer(cleanup)

@pytest.fixture
def client():
    with TestClient(my_app) as c:
        yield c

def test_healthcheck(client):
    response = client.get("/api/v1/healthcheck")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "uptime" in data
    assert isinstance(data["uptime"], dict) 