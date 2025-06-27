# Development Tasks

**Goal**: Implement authentication via OAuth2, using Google as the identity provider.

## 1. Backend - api project

### 1.1. User model

[x] Create a database-backed user model, with the following fields (use `mapped_column` syntax):

- [x] id: UUID
- [x] email: string
- [x] name: string
- [x] last_login: datetime
- [x] is_active: boolean
- [x] is_admin: boolean

[x] Use sqlalchemy for persistence.

### 1.2. Admin CLI Tool

[x] Add a `cli` package under `src/` in the `api` project, starting with an `admin.py` script.

[x] The CLI must be able to import and use any code from the `api` package (e.g., SQLAlchemy models, DB session).
[x] The CLI will be used for admin tasks such as managing users and pre-populating the database from local files.
[x] Update `pyproject.toml` to include both `api` and `cli` as packages:

```toml
[tool.poetry]
packages = [
    {include = "api", from = "src"},
    {include = "cli", from = "src"}
]
```

[x] Add a `[project.scripts]` entry so the CLI can be run as `admin` (calls `main()` in `cli/admin.py`):

```toml
[project.scripts]
admin = "cli.admin:main"
```

[x] The CLI must also be runnable as `python -m cli.admin` (from the correct working directory).
[x] Document both usage options in the README.
[x] Ensure the CLI is future-proofed for additional admin scripts.

#### CLI Help Text and Usage

[x] The help text for the command is:

```text
Usage: python -m cli.admin FLAGS COMMAND OPTIONS

Flags:
  -n             Dry run (do not modify the database, just print what would happen)
  -f             Force overwrite existing entries

Command:
  help           Show this help and exit
  user OPTIONS   add/delete users

Command "user" usage: python -m cli.admin FLAGS user add|del OPTIONS EMAIL

Command "user" options:
  add            Add a user to the user database
  del            Delete a user from the user database
  list           List all users (email, name, and last login datetime)
  -u NAME        set user's name to NAME
  EMAIL          the user's email - this is how the user authenticates.

Examples:

  # Add a user Gert Verhoog with email me@gertalot.com:
  python -m cli.admin user add -u "Gert Verhoog" me@gertalot.com

  # Delete user Gert Verhoog:
  python -m cli.admin user del me@gertalot.com
```

### 1.3. user admin (Done)

[x] In the admin CLI tool, implement the "user" functionality as illustrated above in the help text.

---

### 2. Google OAuth backend (Done)

[x] Implement OAuth2 with Google on the backend API. Create a distinction between public routes and
authenticated routes. The authenticated routes can only be accessed with a successful bearer token (a JWT).

[x] Create a route `/auth/login/google` that initiates the OAuth2 flow with Google. I have configured the following
variables in .env that you can use:

- GOOGLE_CLIENT_ID
- GOOGLE_CLIENT_SECRET
- SESSION_SECRET_KEY
- JWT_SECRET

[x] Create a route `/auth/callback/google` to handle the Oauth2 callback from Google. Detect the original frontend
server the user was using (e.g. <http://localhost>, <https://example.com>, etc) and return a redirect response
to the frontend path `/auth/callback#token={jwt_token}`. We will handle the JWT in the frontend at a later stage.

[x] Create an authenticated route `/auth` that, when authenticated, returns an object representing the user. We will
use this in the frontend to detect if a user is logged in.

#### 2.1. Testing the OAuth Backend (Done)

> **Prompt:**
>
> Write robust, modern test cases for the FastAPI OAuth2 backend using Authlib and pytest. Your tests should:
>
> - Use pytest fixtures and FastAPI's TestClient for all HTTP route tests.
> - Patch/mimic Authlib's `authorize_redirect`, `authorize_access_token`, and `parse_id_token` methods using pytest's `monkeypatch` fixture, so that no real HTTP calls are made to Google.
> - Cover the following flows:
>   1. `/api/v1/auth/login/google` returns a redirect response (302/307) to the Google login page (mocked).
>   2. `/api/v1/auth/callback/google` with mocked token and userinfo creates a user (if new), updates last_login (if existing), and redirects with a JWT in the URL fragment.
>   3. `/api/v1/auth` returns 401 if no/invalid JWT, and returns user info if a valid JWT is provided.
>   4. Error cases: OAuth error, missing userinfo, invalid JWT, user not found.
> - Use fixtures to set up the test DB and client, and ensure all tests are isolated and repeatable.
> - Assert on all relevant response status codes, headers, and payloads.
> - Use best practices for dependency injection and mocking, and ensure all code is clean, readable, and up-to-date with 2024 best practices.
> - Do not use any real network calls or external dependencies in tests.
> - Ensure all new code is covered by automated tests, and all tests pass cleanly.

---

### Auth frontend
