# Savour Herbs Database

## Prerequisites

- Docker
- Docker Compose

## Usage

### Start the database

```sh
docker compose up -d
```

### Stop the database

```sh
docker compose down
```

### Data Persistence

- Data is stored in the named Docker volume `herbs-data`.

### Connection Details

- Username, password, and database name are set in `docker-compose.yml`.
- The full connection string is stored in the `.env` file in the `api` project.
- Default port: 5432
