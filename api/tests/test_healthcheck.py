import os
import pathlib
# Set dummy env vars before importing app/auth
os.environ["GOOGLE_CLIENT_ID"] = "dummy-client-id"
os.environ["GOOGLE_CLIENT_SECRET"] = "dummy-client-secret"
os.environ["JWT_SECRET"] = "dummy-jwt-secret"
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

# Clean up test.db before and after tests
TEST_DB_PATH = pathlib.Path("./test.db")
if TEST_DB_PATH.exists():
    TEST_DB_PATH.unlink()

from fastapi.testclient import TestClient
from app import my_app as app
print(f"[DEBUG] my_app imported from: {app.__module__}, id: {id(app)}")
from fastapi.routing import APIRoute
print("[DEBUG] Registered routes:")
for route in app.routes:
    if isinstance(route, APIRoute):
        print(f"[DEBUG] {route.path} [{', '.join(route.methods)}]")
from app.db import get_engine, Base
import pytest
from unittest.mock import patch, AsyncMock

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
    with TestClient(app) as c:
        yield c

def test_healthcheck():
    client = TestClient(app)
    response = client.get("/api/v1/healthcheck")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "uptime" in data
    assert isinstance(data["uptime"], dict)

def test_auth_routes_exist(client):
    resp = client.get("/api/v1/auth/login/google")
    print(f"[DEBUG] /api/v1/auth/login/google response: {resp.status_code} {resp.text}")
    assert resp.status_code in (200, 307, 302)  # Should redirect or OK
    resp2 = client.get("/api/v1/auth")
    assert resp2.status_code == 401  # No token provided

def test_auth_callback_google_mocked(client):
    """Test /api/v1/auth/callback/google with mocked OAuth flow."""
    with patch("app.auth.oauth.google.authorize_access_token", new=AsyncMock(return_value={"id_token": "dummy"})), \
         patch("app.auth.oauth.google.parse_id_token", new=AsyncMock(return_value={
             "email": "testuser@example.com",
             "name": "Test User"
         })):
        # Simulate the callback request
        response = client.get("/api/v1/auth/callback/google", headers={"origin": "http://localhost:3000"})
        # Should redirect to frontend with a token in the fragment
        assert response.status_code in (302, 307)
        assert response.headers["location"].startswith("http://localhost:3000/auth/callback#token=") 