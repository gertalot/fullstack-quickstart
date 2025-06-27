# Makefile for monorepo: backend (api), frontend (web), db, and release automation

.PHONY: help build test lint clean app-clean web-clean app-test app-dev app-install app-build app-lint admin web-test web-dev web-install web-build web-lint db-dev release release-latest

help:
	@echo "Available targets:"
	@echo "  build           Build and package all projects for deployment"
	@echo "  test            Run all tests"
	@echo "  lint            Lint and type-check the codebase"
	@echo "  clean           Remove build artifacts and caches from all subprojects"
	@echo "  app-clean       Clean backend (api) build artifacts and caches"
	@echo "  web-clean       Clean frontend (web) build artifacts and caches"
	@echo "  app-test        Run backend tests with pytest"
	@echo "  app-dev         Start backend dev server (uvicorn, hot reload)"
	@echo "  app-install     Install backend dependencies"
	@echo "  app-build       Build backend (customize as needed)"
	@echo "  app-lint        Lint and type-check the backend codebase"
	@echo "  admin           Run TEMPLATE_CLI_NAME CLI in the api directory (forwards all arguments)"
	@echo "  web-test        Run frontend tests with vitest"
	@echo "  web-dev         Start frontend dev server (vite/next)"
	@echo "  web-install     Install frontend dependencies"
	@echo "  web-build       Build frontend (customize as needed)"
	@echo "  web-lint        Lint and type-check the frontend codebase"
	@echo "  db-dev          Start database with Docker Compose"
	@echo "  release         Create a versioned release tarball and upload to GitHub Releases"
	@echo "  release-latest  Create a tarball for the latest release (template-latest.tar.gz)"

# Aggregate targets
install: app-install web-install
	@echo "Installed all dependencies"

build: app-build web-build
	@echo "All projects built!"

test: app-test web-test
	@echo "Ran all tests"

lint: app-lint web-lint
	@echo "Linted and type-checked the codebase"

clean: app-clean web-clean
	@echo "Cleaned all subprojects."

# API (backend) targets
app-test:
	cd api && poetry run pytest

app-dev:
	cd api && poetry run uvicorn app:my_app --host 0.0.0.0 --reload

app-install:
	cd api && poetry install

app-build:
	cd api && echo "Build backend here"

app-lint:
	cd api && poetry run ruff check . && poetry run mypy .

app-clean:
	rm -rf api/__pycache__ api/.mypy_cache api/.ruff_cache api/.pytest_cache api/dist api/build api/.venv
	find api -name '*.pyc' -delete
	@echo "Cleaned backend (api) build artifacts and caches."

admin:
	cd api && poetry run TEMPLATE_CLI_NAME $(ARGS)

# Web (frontend) targets
web-test:
	cd web && yarn test

web-dev:
	cd web && yarn dev

web-install:
	cd web && yarn install

web-build:
	cd web && yarn build

web-lint:
	cd web && yarn lint && yarn tsc --noEmit

web-clean:
	rm -rf web/.next web/dist web/build web/coverage web/node_modules
	@echo "Cleaned frontend (web) build artifacts and caches."

# DB targets
db-dev:
	cd db && docker compose up

# Release automation
release:
	$(eval VERSION := $(shell grep '^version =' api/pyproject.toml | cut -d'"' -f2))
	git tag "v$(VERSION)"
	git push origin "v$(VERSION)"
	tar --exclude='.git' --exclude='.venv' --exclude='node_modules' --exclude='__pycache__' --exclude='*.pyc' --exclude='*.log' --exclude="template-$(VERSION).tar.gz" -czf "template-$(VERSION).tar.gz" .
	gh release create "v$(VERSION)" "template-$(VERSION).tar.gz" --title "v$(VERSION)" --notes "Release $(VERSION)"

release-latest:
	tar --exclude='.git' --exclude='.venv' --exclude='node_modules' --exclude='__pycache__' --exclude='*.pyc' --exclude='*.log' -czf "template-latest.tar.gz" . 