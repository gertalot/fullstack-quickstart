set dotenv-load
set shell := ["/bin/zsh", "-cu"]

help:
    just --list api
    
dev:
    cd api && poetry run uvicorn api:app --reload

install:
    cd api && poetry install

test:
    cd api && poetry run pytest

lint:
    cd api && poetry run ruff check .
