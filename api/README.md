# Savour Herbs API

## Prerequisites

- Python 3.11
- Poetry

## Installation

```sh
poetry install
```

## Activate the virtual environment

```sh
poetry shell
```

## Running the development server

```sh
uvicorn api:app --reload --factory
```

- The API will be available at <http://localhost:8000/api/v1/healthcheck>

## Testing

```sh
pytest
```
