# Mellow Loader Blueprint (Peccary Docker)

This directory is a working example of a mellow loader application.

## Purpose

The loader reads validated JSON files from a fresh directory, records accepted files in PostgreSQL, and then removes the processed JSON from local storage.

Unlike wombat, this process runs on a different machine and retains upstream source archives separately. Deleting successfully processed JSON files is intentional.

## Components

### 1) Application Entrypoint

File: slug_app.py

- Builds database connectivity from environment variables.
- Configures SQLAlchemy engine options (connection timeout, statement timeout, pool pre-ping).
- Routes execution by stuntbox mode.
- Current mode: loader.

### 2) Loader Engine

File: loader.py

- Iterates files in the configured fresh directory.
- Uses JsonHelper to validate file structure and content.
- Enforces idempotency by checking load-log storage by file name.
- On success: inserts load-log and daily-score rows, then deletes local file.
- On failure: moves file to failure directory.
- Tracks run counters for success and failure outcomes.

### 3) Persistence Layer

Files: ../helper/postgres.py and ../helper/sql_table.py

- Implements data access methods used by the loader.
- Uses slug_geo_loc lookup records for referential integrity.
- Writes slug_load_log and updates slug_daily_score.

## Runtime Configuration

Supported environment variables:

1. DB_CONN
2. PG_CONNECT_TIMEOUT (default 5)
3. PG_STATEMENT_TIMEOUT_MS (default 5000)
4. FRESH_DIR (default /var/peccary/hyena/hyena-v2)
5. FAILURE_DIR (default /var/peccary/hyena/failure)
6. stuntbox (default loader)

## Local Run Pattern

```bash
cd src/peccary_docker
source venv/bin/activate
pip install -r requirements.txt
python slug_app.py
```

## Testing

Run tests from src/peccary_docker/pytest.sh

## Docker Run Pattern

Build:

```bash
docker build -f src/peccary_docker/Dockerfile -t slug:latest src/
```

Run:

```bash
docker run \
	-e stuntbox=loader \
	-e DB_CONN="postgresql+psycopg2://slug_client:batabat@172.17.0.1:5432/slug" \
	-v /var/peccary:/mnt/peccary \
	--name slug \
	slug:latest
```

