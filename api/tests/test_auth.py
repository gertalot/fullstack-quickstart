import os
import pathlib
import pytest
from fastapi.testclient import TestClient
from app import my_app
from app.db import get_engine, Base, get_session
from app.models import User
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuthError
import uuid
import app.auth as auth_mod

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

def create_jwt_for_user(user: User) -> str:
    import datetime
    from jose import jwt
    payload = {
        "sub": str(user.id),
        "email": user.email,
        "name": user.name,
        "is_admin": user.is_admin,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=12),
    }
    jwt_secret = os.environ.get("JWT_SECRET", "changeme")
    jwt_algorithm = "HS256"
    return jwt.encode(payload, jwt_secret, algorithm=jwt_algorithm)

@pytest.fixture
def mock_authorize_redirect(monkeypatch):
    async def fake_authorize_redirect(request, redirect_uri):
        return RedirectResponse(url="/somewhere", status_code=302)
    monkeypatch.setattr(auth_mod.oauth.google, "authorize_redirect", fake_authorize_redirect)

@pytest.fixture
def mock_authorize_access_token(monkeypatch):
    async def fake_authorize_access_token(request):
        return {"id_token": "dummy"}
    monkeypatch.setattr(auth_mod.oauth.google, "authorize_access_token", fake_authorize_access_token)

@pytest.fixture
def mock_parse_id_token(monkeypatch):
    async def fake_parse_id_token(request, token):
        return {"email": "testuser@example.com", "name": "Test User"}
    monkeypatch.setattr(auth_mod.oauth.google, "parse_id_token", fake_parse_id_token)

@pytest.fixture
def mock_parse_id_token_existing(monkeypatch):
    async def fake_parse_id_token(request, token):
        return {"email": "existing@example.com", "name": "New Name"}
    monkeypatch.setattr(auth_mod.oauth.google, "parse_id_token", fake_parse_id_token)

@pytest.fixture
def mock_authorize_access_token_oauth_error(monkeypatch):
    async def fake_authorize_access_token(request):
        raise OAuthError("OAuth failed")
    monkeypatch.setattr(auth_mod.oauth.google, "authorize_access_token", fake_authorize_access_token)

@pytest.fixture
def mock_parse_id_token_none(monkeypatch):
    async def fake_parse_id_token(request, token):
        return None
    monkeypatch.setattr(auth_mod.oauth.google, "parse_id_token", fake_parse_id_token)

def test_auth_login_google_redirect(client, mock_authorize_redirect):
    resp = client.get("/api/v1/auth/login/google", follow_redirects=False)
    assert resp.status_code in (302, 307)
    assert resp.headers["location"] == "/somewhere"

def test_auth_callback_google_creates_and_returns_jwt(client, mock_authorize_access_token, mock_parse_id_token):
    resp = client.get("/api/v1/auth/callback/google", headers={"origin": "http://localhost:3000"}, follow_redirects=False)
    assert resp.status_code in (302, 307)
    assert resp.headers["location"].startswith("http://localhost:3000/auth/callback#token=")
    engine = get_engine()
    session = get_session(engine)
    user = session.query(User).filter_by(email="testuser@example.com").first()
    assert user is not None
    assert user.name == "Test User"
    assert user.is_active
    assert not user.is_admin

def test_auth_callback_google_updates_existing_user(client, mock_authorize_access_token, mock_parse_id_token_existing):
    engine = get_engine()
    session = get_session(engine)
    user = User(email="existing@example.com", name="Old Name", is_active=True, is_admin=False)
    session.add(user)
    session.commit()
    old_last_login = user.last_login
    resp = client.get("/api/v1/auth/callback/google", headers={"origin": "http://localhost:3000"}, follow_redirects=False)
    assert resp.status_code in (302, 307)
    session.refresh(user)
    assert user.name == "New Name"
    assert user.last_login is not None
    assert user.last_login != old_last_login

def test_auth_callback_google_oauth_error(client, mock_authorize_access_token_oauth_error):
    resp = client.get("/api/v1/auth/callback/google", headers={"origin": "http://localhost:3000"})
    assert resp.status_code == 400
    assert "OAuth authentication failed" in resp.text or "OAuth failed" in resp.text

def test_auth_callback_google_missing_userinfo(client, mock_authorize_access_token, mock_parse_id_token_none):
    resp = client.get("/api/v1/auth/callback/google", headers={"origin": "http://localhost:3000"})
    assert resp.status_code == 400
    assert "Failed to retrieve user info" in resp.text

def test_auth_protected_route_requires_jwt(client):
    resp = client.get("/api/v1/auth")
    assert resp.status_code == 401
    assert "Missing or invalid Authorization header" in resp.text

def test_auth_protected_route_with_valid_jwt(client):
    engine = get_engine()
    session = get_session(engine)
    user = User(email="jwtuser@example.com", name="JWT User", is_active=True, is_admin=True)
    session.add(user)
    session.commit()
    token = create_jwt_for_user(user)
    resp = client.get("/api/v1/auth", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == "jwtuser@example.com"
    assert data["is_admin"] is True

def test_auth_protected_route_with_invalid_jwt(client):
    resp = client.get("/api/v1/auth", headers={"Authorization": "Bearer invalidtoken"})
    assert resp.status_code == 401
    assert "Invalid token" in resp.text

def test_print_all_routes(client):
    for route in client.app.routes:
        print(f"{route.path} -> {getattr(route, 'methods', None)}")

def test_minimal_redirect(client):
    resp = client.get("/api/v1/test-redirect", follow_redirects=False)
    assert resp.status_code == 302
    assert resp.headers["location"] == "/api/v1/healthcheck"

def test_mocked_async_redirect(client):
    resp = client.get("/api/v1/test-redirect-mock", follow_redirects=False)
    assert resp.status_code == 302
    assert resp.headers["location"] == "/api/v1/healthcheck" 