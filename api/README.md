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

## Admin CLI Usage

You can run the admin CLI in two ways:

1. As an installed script (after 'poetry install' or 'pip install .'):

    savour-admin [FLAGS] COMMAND [OPTIONS]

2. Directly with Python (from the api/src directory):

    python -m cli.admin [FLAGS] COMMAND [OPTIONS]

The CLI supports managing users and uploading herb data. See the help text for details and examples.
