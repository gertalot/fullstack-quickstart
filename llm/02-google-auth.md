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

[x] Add a `[project.scripts]` entry so the CLI can be run as `savour-admin` (calls `main()` in `cli/admin.py`):

```toml
[project.scripts]
savour-admin = "cli.admin:main"
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
  herbs OPTIONS  upload herb information to the database
  user OPTIONS   add/delete users

Command "herbs" usage: python -m cli.admin FLAGS herbs OPTIONS

herbs Options:
  -d DIR         Directory containing images (mandatory)
  -i YAML_FILE   YAML file with herb entries (mandatory)

Command "user" usage: python -m cli.admin FLAGS user add|del OPTIONS EMAIL

Command "user" options:
  add            Add a user to the user database
  del            Delete a user from the user database
  list           List all users (email, name, and last login datetime)
  -u NAME        set user's name to NAME
  EMAIL          the user's email - this is how the user authenticates.

Examples:

  # Load all herbs and images from cards.yaml into the herbs table:
  python -m cli.admin herbs -d ./images -i ./cards.yaml

  # Add a user Gert Verhoog with email me@gertalot.com:
  python -m cli.admin user add -u "Gert Verhoog" me@gertalot.com

  # Delete user Gert Verhoog:
  python -m cli.admin user del me@gertalot.com
```

### 1.3. user admin (Done)

[x] In the admin CLI tool, implement the "user" functionality as illustrated above in the help text.

---

### 2. Google OAuth backend

Implement OAuth2 with Google on the backend API. Create a distinction between public routes and
authenticated routes. The authenticated routes can only be accessed with a successful bearer token (a JWT).

Create a route `/auth/login/google` that initiates the OAuth2 flow with Google. I have configured the following
variables in .env that you can use:

- GOOGLE_CLIENT_ID
- GOOGLE_CLIENT_SECRET
- SESSION_SECRET_KEY
- JWT_SECRET

Create a route `/auth/callback/google` to handle the Oauth2 callback from Google. Detect the original frontend
server the user was using (e.g. <http://localhost>, <https://example.com>, etc) and return a redirect response
to the frontend path `/auth/callback#token={jwt_token}`. We will handle the JWT in the frontend at a later stage.

Create an authenticated route `/auth` that, when authenticated, returns an object representing the user. We will
use this in the frontend to detect if a user is logged in.
