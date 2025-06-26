# Set the working directory to the directory where the Justfile is located
set dotenv-load
set shell := ["/bin/zsh", "-cu"]

help:
    just --list

mod api
mod web
mod db

