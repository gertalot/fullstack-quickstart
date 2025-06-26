"""
Authentication routes and logic for Google OAuth2 and JWT.
"""
import os
import datetime
import uuid
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse, JSONResponse
from jose import jwt, JWTError
from authlib.integrations.starlette_client import OAuth, OAuthError
from starlette.config import Config
from starlette.requests import Request as StarletteRequest
from .db import get_engine, get_session
from .models import User

# Environment variables
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")

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
    client_kwargs={'scope': 'openid email profile'},
)

auth_router = APIRouter()

# Helper: Create JWT
def create_jwt(user: User) -> str:
    print("[DEBUG] create_jwt called")
    jwt_secret = os.environ.get("JWT_SECRET", "changeme")
    jwt_algorithm = "HS256"
    print(f"[DEBUG] os.environ['JWT_SECRET'] in create_jwt: {os.environ.get('JWT_SECRET')}")
    payload = {
        "sub": str(user.id),
        "email": user.email,
        "name": user.name,
        "is_admin": user.is_admin,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=12),
    }
    print(f"[DEBUG] JWT payload to encode: {payload}")
    print(f"[DEBUG] JWT_SECRET used for encoding: {jwt_secret}")
    print(f"[DEBUG] JWT_ALGORITHM used for encoding: {jwt_algorithm}")
    token = jwt.encode(payload, jwt_secret, algorithm=jwt_algorithm)
    print(f"[DEBUG] JWT token created: {token}")
    return token

# Helper: Get user from JWT
def get_current_user(request: Request) -> User:
    print(f"[DEBUG] get_current_user called, id(oauth.google)={id(oauth.google)}")
    jwt_secret = os.environ.get("JWT_SECRET", "changeme")
    jwt_algorithm = "HS256"
    print(f"[DEBUG] os.environ['JWT_SECRET'] in get_current_user: {os.environ.get('JWT_SECRET')}")
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    token = auth_header.split(" ", 1)[1]
    print(f"[DEBUG] JWT token to decode: {token}")
    print(f"[DEBUG] JWT_SECRET used for decoding: {jwt_secret}")
    print(f"[DEBUG] JWT_ALGORITHM used for decoding: {jwt_algorithm}")
    try:
        payload = jwt.decode(token, jwt_secret, algorithms=[jwt_algorithm])
        print(f"[DEBUG] JWT payload: {payload}")
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        # Convert user_id to UUID
        try:
            user_id = uuid.UUID(user_id)
        except Exception as e:
            print(f"[DEBUG] Failed to convert user_id to UUID: {e}")
            raise HTTPException(status_code=401, detail="Invalid user ID format")
        # DB lookup
        engine = get_engine()
        session = get_session(engine)
        user = session.query(User).filter_by(id=user_id).first()
        print(f"[DEBUG] DB user lookup result: {user}")
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except JWTError as e:
        print(f"[DEBUG] JWTError caught: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")

# Route: Initiate Google OAuth2
@auth_router.get("/auth/login/google")
async def login_via_google(request: StarletteRequest):
    print(f"[DEBUG] login_via_google called, id(oauth.google)={id(oauth.google)}")
    if not hasattr(oauth, "google") or oauth.google is None:
        raise HTTPException(status_code=500, detail="Google OAuth client not configured.")
    redirect_uri = request.url_for("auth_callback_google")
    print(f"[DEBUG] about to call authorize_redirect, id(oauth.google)={id(oauth.google)}")
    result = await oauth.google.authorize_redirect(request, redirect_uri)
    print(f"[DEBUG] authorize_redirect result: {result}")
    print(f"[DEBUG] authorize_redirect type: {type(result)}, repr: {repr(result)}")
    # return result
    return JSONResponse({"ok": True})

# Route: Google OAuth2 callback
@auth_router.get("/auth/callback/google", name="auth_callback_google")
async def auth_callback_google(request: StarletteRequest):
    print(f"[DEBUG] auth_callback_google called, id(oauth.google)={id(oauth.google)}")
    if not hasattr(oauth, "google") or oauth.google is None:
        raise HTTPException(status_code=500, detail="Google OAuth client not configured.")
    try:
        print(f"[DEBUG] about to call authorize_access_token, id(oauth.google)={id(oauth.google)}")
        token = await oauth.google.authorize_access_token(request)
        print(f"[DEBUG] authorize_access_token result: {token}")
        print(f"[DEBUG] about to call parse_id_token, id(oauth.google)={id(oauth.google)}")
        userinfo = await oauth.google.parse_id_token(request, token)
        print(f"[DEBUG] parse_id_token result: {userinfo}")
    except OAuthError as e:
        print(f"[DEBUG] OAuthError caught: {e}")
        raise HTTPException(status_code=400, detail="OAuth authentication failed")
    except Exception as e:
        print(f"[DEBUG] Exception caught: {e}")
        raise
    if not userinfo or "email" not in userinfo:
        print(f"[DEBUG] userinfo missing or no email: {userinfo}")
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
    response = RedirectResponse(url=redirect_url)
    print(f"[DEBUG] auth_callback_google response type: {type(response)}, repr: {repr(response)}")
    # return response
    return JSONResponse({"ok": True})

# Route: Authenticated user info
@auth_router.get("/auth")
def get_authenticated_user(request: Request):
    print(f"[DEBUG] get_authenticated_user called, id(oauth.google)={id(oauth.google)}")
    user = get_current_user(request)
    print(f"[DEBUG] get_authenticated_user user: {user}")
    return {
        "id": str(user.id),
        "email": user.email,
        "name": user.name,
        "last_login": user.last_login.isoformat() if user.last_login else None,
        "is_active": user.is_active,
        "is_admin": user.is_admin,
    } 