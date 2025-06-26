set dotenv-load
set shell := ["/bin/zsh", "-cu"]

help:
    just --list db

dev:
    cd db && docker compose up
