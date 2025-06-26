"""
Authentication routes and logic for Google OAuth2 and JWT.
"""
import os
import uuid
import datetime
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from authlib.integrations.starlette_client import OAuth, OAuthError
from starlette.config import Config
from starlette.requests import Request as StarletteRequest
from .db import get_engine, get_session
from .models import User

# Environment variables
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
JWT_SECRET = os.environ.get("JWT_SECRET", "changeme")
JWT_ALGORITHM = "HS256"

# OAuth setup
config = Config(environ={
    "GOOGLE_CLIENT_ID": GOOGLE_CLIENT_ID or "",
    "GOOGLE_CLIENT_SECRET": GOOGLE_CLIENT_SECRET or "",
})
oauth = OAuth(config)
oauth.register(
    name='google',
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile',
    },
)

auth_router = APIRouter()

# Helper: Create JWT
def create_jwt(user: User) -> str:
    payload = {
        "sub": str(user.id),
        "email": user.email,
        "name": user.name,
        "is_admin": user.is_admin,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=12),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

# Helper: Get user from JWT
def get_current_user(request: Request) -> User:
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    token = auth_header.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        # DB lookup
        engine = get_engine()
        session = get_session(engine)
        user = session.query(User).filter_by(id=user_id).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Route: Initiate Google OAuth2
@auth_router.get("/auth/login/google")
async def login_via_google(request: StarletteRequest):
    """Initiate Google OAuth2 login flow."""
    if not hasattr(oauth, "google") or oauth.google is None:
        raise HTTPException(status_code=500, detail="Google OAuth client not configured.")
    redirect_uri = request.url_for("auth_callback_google")
    return await oauth.google.authorize_redirect(request, redirect_uri)  # type: ignore[attr-defined]

# Route: Google OAuth2 callback
@auth_router.get("/auth/callback/google", name="auth_callback_google")
async def auth_callback_google(request: StarletteRequest):
    """Handle Google OAuth2 callback and issue JWT."""
    if not hasattr(oauth, "google") or oauth.google is None:
        raise HTTPException(status_code=500, detail="Google OAuth client not configured.")
    try:
        token = await oauth.google.authorize_access_token(request)  # type: ignore[attr-defined]
        userinfo = await oauth.google.parse_id_token(request, token)  # type: ignore[attr-defined]
    except OAuthError:
        raise HTTPException(status_code=400, detail="OAuth authentication failed")
    if not userinfo or "email" not in userinfo:
        raise HTTPException(status_code=400, detail="Failed to retrieve user info from Google")
    # DB: Find or create user
    engine = get_engine()
    session = get_session(engine)
    user = session.query(User).filter_by(email=userinfo["email"]).first()
    if not user:
        user = User(
            email=userinfo["email"],
            name=userinfo.get("name", userinfo["email"]),
            last_login=datetime.datetime.utcnow(),
            is_active=True,
            is_admin=False,
        )
        session.add(user)
    else:
        user.last_login = datetime.datetime.utcnow()
        user.name = userinfo.get("name", user.name)
    session.commit()
    # JWT
    jwt_token = create_jwt(user)
    # Detect frontend origin
    origin = request.headers.get("origin") or os.environ.get("FRONTEND_ORIGIN", "http://localhost:3000")
    redirect_url = f"{origin}/auth/callback#token={jwt_token}"
    return RedirectResponse(url=redirect_url)

# Route: Authenticated user info
@auth_router.get("/auth")
def get_authenticated_user(request: Request):
    user = get_current_user(request)
    return {
        "id": str(user.id),
        "email": user.email,
        "name": user.name,
        "last_login": user.last_login.isoformat() if user.last_login else None,
        "is_active": user.is_active,
        "is_admin": user.is_admin,
    } 