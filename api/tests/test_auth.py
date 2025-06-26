import os
import pathlib
import pytest
from fastapi.testclient import TestClient
from app import my_app
from app.db import get_engine, Base
from unittest.mock import patch, AsyncMock

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

def test_auth_routes_exist(client):
    resp = client.get("/api/v1/auth/login/google")
    assert resp.status_code in (200, 307, 302)
    resp2 = client.get("/api/v1/auth")
    assert resp2.status_code == 401

def test_auth_callback_google_mocked(client):
    with patch("app.auth.oauth.google.authorize_access_token", new=AsyncMock(return_value={"id_token": "dummy"})), \
         patch("app.auth.oauth.google.parse_id_token", new=AsyncMock(return_value={
             "email": "testuser@example.com",
             "name": "Test User"
         })):
        response = client.get("/api/v1/auth/callback/google", headers={"origin": "http://localhost:3000"})
        assert response.status_code in (302, 307)
        assert response.headers["location"].startswith("http://localhost:3000/auth/callback#token=") 