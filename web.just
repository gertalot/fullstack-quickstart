set dotenv-load
set shell := ["/bin/zsh", "-cu"]

help:
    just --list web

dev:
    cd web && yarn dev

install:
    cd web && yarn install

test:
    cd web && yarn test

lint:
    cd web && yarn lint
