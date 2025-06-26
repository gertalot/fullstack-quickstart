# Development Tasks (Done)

## 1. Create Basic Project Scaffolding (Done)

Focus on local development only.

### 1.1. Backend API (Done)

- [x] Create a new Python project in the `api` subdirectory using `poetry new api`.
- [x] Set up a local `.venv` for the virtual environment and activate it.
- [x] Ensure that Cursor and VSCode use the Python interpreter from `.venv`.
- [x] All API routes must be served under `/api/v1` using FastAPI's router mounting: `app.include_router(router, prefix="/api/v1")`.
- [x] Implement a `healthcheck` endpoint at `/api/v1/healthcheck` that returns HTTP 200 and a JSON object with `message` and `uptime` (uptime should be dynamic, calculated since the server started).
- [x] Use `pytest` for backend testing. Add a sample test for the healthcheck endpoint.
- [x] Create a `README.md` in `api` describing prerequisites, installation, and how to run the development server.

### 1.2. Database (Done)

- [x] Create a `db` subdirectory.
- [x] Add a Docker Compose file to start a Postgres database with data persisted on a named volume `herbs-data`.
- [x] Generate a strong username and password for the database.
- [x] Store the full Postgres connection string in a `.env` file as `DATABASE_URL` for the API backend project.
- [x] Create a `README.md` in `db` describing prerequisites, installation, and how to run the database locally.

### 1.3. Frontend (Done)

- [x] Create a `web` subdirectory using:

```sh
npx create-next-app@latest web \
  --ts --tailwind --eslint --app --src-dir --turbopack --no-import-alias --use-yarn
```

- [x] Use ESLint and Prettier.
- [x] Use TailwindCSS for styling.
- [x] Set up vitest for unit testing and component testing.
- [x] Implement a simple home page with a dark theme and a centered component that:
  - Calls `/api/v1/healthcheck`.
  - If 200 OK, displays the message in green.
  - If not 200 OK, displays the message in orange with the status code, and the returned message in smaller font below.
  - Below, in small font, display the uptime as "Live since x days, y hours, z minutes".
- [x] Create a `README.md` in `web` describing prerequisites, installation, and how to run the development server.
