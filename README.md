# Project Template Quick Start

This repository is a full-stack web application template (Next.js + FastAPI + PostgreSQL) ready for customization.

## 🚀 Getting Started

You can initialize your new project from this template using the provided script. This will replace all template variables in the codebase and set up your project for development.

### 1. Download and Run the Initializer

**Interactive mode (recommended):**

```sh
curl -sSL https://example.com/init-template.sh | zsh
```

You will be prompted for all required project details.

**Non-interactive mode:**

```sh
curl -sSL https://example.com/init-template.sh | zsh -- \
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
  - `TEMPLATE_CLI_NAME`
  - `TEMPLATE_DOCKER_VOLUME`
- Replaces all template variables in the codebase
- Optionally renames files/directories containing template variables
- Removes the `.git` directory (with confirmation)
- Initializes a new git repository
- Removes itself after running

### 3. Next Steps

- Install dependencies for backend and frontend as described in their respective `README.md` files
- Start developing your new project!

---

[Continue with your own project documentation below...]
