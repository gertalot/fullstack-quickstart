# Full Stack Quickstart

This repository is a full-stack web application with FastAPI, NextJS, and Postgres, ready for customisation.

## TL;DR

```sh
curl -sSL https://raw.githubusercontent.com/gertalot/fullstack-quickstart/main/script/init.sh | sh
```

Then answer some questions about your project, and voila! To make sure it's all working:

```sh
cd fullstack-quickstart
make install test
```

## Features

These are basic features you can build on or replace with something else:

- **Backend**
  - Python, FastAPI, poetry
  - supports Google OAuth authentication flow.
  - `/api/v1/auth` route returns information about the authenticated user
  - `/healthcheck` returns a health check status + uptime
  - SQLAlchemy for persistence, with `User` object for authorised users
  - command line `admin` tool to manage users outside of the api
  - tests with pytest
- **Storage**
  - Postgres database running in a docker container
- **Frontend**
  - Typescript, NextJS, Tailwind, Vitest
  - main page that calls the healthcheck API route
  - tests with vitest

## AI-Driven Coding Template

This repository is designed for AI-driven development workflows. It includes:

- **Custom rules in `.cursor/`**: These provide project context, coding style guidelines, and other metadata to guide AI
  coding assistants (like Cursor, Copilot, or GPT-based tools).
- **Task-driven development**: To add new features or make changes, simply add a markdown file describing your
  development task to the `llm/` directory. The AI model will read and execute these tasks iteratively.
- **Full-stack template**: The repo is structured as a monorepo with backend (`api`), frontend (`web`), and database
  (`db`) projects, all ready for AI-assisted or human development.

## Project Structure

This monorepo contains three subprojects:

- **api/** – The backend API
  - **Tech stack:** Python 3.x, FastAPI, SQLAlchemy, Poetry, Uvicorn, Pytest
  - **Purpose:** Provides a RESTful API for managing entities and their properties, authentication, and business logic.
    All backend logic and database access live here.

- **db/** – The database and infrastructure
  - **Tech stack:** PostgreSQL (via Docker Compose)
  - **Purpose:** Contains database configuration, Docker Compose setup, and related infrastructure scripts. Manages
    persistent data storage for the application.

- **web/** – The frontend web application
  - **Tech stack:** TypeScript, Next.js, React, TailwindCSS, Vite, ESLint, Vitest
  - **Purpose:** User-facing web interface for interacting with the application, displaying and managing entities, and
    generating printable PDF cards.

## Getting Started

You can initialize your new project from this template using the provided script. This will replace all template
variables in the codebase and set up your project for development.

### 1. Download and Run the Initializer

**Interactive mode (recommended):**

```sh
curl -sSL https://raw.githubusercontent.com/gertalot/fullstack-quickstart/main/script/init.sh | sh
```

You will be prompted for all required project details.

**Non-interactive mode:**

```sh
curl -sSL https://raw.githubusercontent.com/gertalot/fullstack-quickstart/main/script/init.sh | sh -- \
  -n "MyApp" \
  -a "Jane Doe" \
  -e "jane.doe@example.com" \
  -d "myapp_db" \
  -c "myapp-admin" \
  -v "myapp-data"
```

### 2. What the Script Does

- Prompts for or accepts via CLI the following variables:
  - `TEMPLATE_PROJECT_NAME`
  - `TEMPLATE_AUTHOR_NAME`
  - `TEMPLATE_AUTHOR_EMAIL@EXAMPLE.COM`
  - `TEMPLATE_DB_NAME`
  - `TEMPLATE_DOCKER_VOLUME`
- Replaces all template variables in the codebase
- Optionally renames files/directories containing template variables
- Removes the `.git` directory (with confirmation)
- Initializes a new git repository
- Removes itself after running

### 3. Next Steps

- Install dependencies for backend and frontend as described in their respective `README.md` files
- Start developing your new project!

## Development Workflow

You can use the provided Makefile to build, lint, test, and run development servers for each subproject:

### Build All Projects

```sh
make build
```

### Lint All Projects

```sh
make lint
```

### Run All Tests

```sh
make test
```

### Backend (API)

- Install dependencies: `make app-install`
- Run dev server: `make app-dev`
- Lint: `make app-lint`
- Test: `make app-test`
- Build: `make app-build`

### Frontend (Web)

- Install dependencies: `make web-install`
- Run dev server: `make web-dev`
- Lint: `make web-lint`
- Test: `make web-test`
- Build: `make web-build`

### Database

- Start database (Docker): `make db-dev`

See `make help` for a full list of available commands.

## License

This project template is licensed under the [MIT License](./LICENSE).
