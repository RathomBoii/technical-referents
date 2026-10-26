# ecommerce_backoffice API

FastAPI service with user endpoints, backed by PostgreSQL.

| Method | Path | Description |
| --- | --- | --- |
| POST | `/users` | Create a user |
| GET | `/users/{user_id}` | Get a user by id |
| DELETE | `/users/{user_id}` | Delete a user by id |

## Prerequisites

- Python >= 3.15 and [uv](https://docs.astral.sh/uv/)
- Docker (for the databases)

Install dependencies:

```bash
uv sync
```

## 1. Start the databases

Run two separate Postgres containers: one for development, one for tests.
The tests drop their tables when they finish, so never point them at the dev database.

Dev (port 5432):

```bash
docker run -d --name ecommerce \
  -e POSTGRES_USER=user_service \
  -e POSTGRES_PASSWORD=secret \
  -e POSTGRES_DB=user \
  -p 5432:5432 \
  postgres:18
```

Test (port 5433):

```bash
docker run -d --name ecommerce-test \
  -e POSTGRES_USER=user_service_test \
  -e POSTGRES_PASSWORD=secret \
  -e POSTGRES_DB=user_test \
  -p 5433:5432 \
  postgres:18
```

Start them again later with `docker start ecommerce ecommerce-test`.

## 2. Configure environment variables

The app builds its database URL from separate variables (see `infrastructure/config.py`),
so the password is escaped for you. uv does not load a `.env` file on its own: pass it with `--env-file`.

Create `.env` for dev:

```dotenv
DB_HOST=localhost
DB_PORT=5432
DB_NAME=user
DB_USER=user_service
DB_PASSWORD=secret
```

Create `.env.test` for tests (same variable names, test database values):

```dotenv
DB_HOST=localhost
DB_PORT=5433
DB_NAME=user_test
DB_USER=user_service_test
DB_PASSWORD=secret
```

Both files hold secrets and must stay out of git (`.env` is already in `.gitignore`).

## 3. Run the server

```bash
uv run --env-file .env fastapi dev src/ecommerce_backoffice/main.py
```

- API: <http://127.0.0.1:8000>
- Swagger UI: <http://127.0.0.1:8000/docs>
- OpenAPI schema: <http://127.0.0.1:8000/openapi.json>

The `users` table is created on startup (`Base.metadata.create_all`).
This does not migrate existing tables: if a column changes, drop the table or add a migration tool.

## Run the tests

Tests need the test database variables, so load `.env.test`:

```bash
# DTO level
uv run --env-file .env.test pytest src/ecommerce_backoffice/controller/dto

# Domain level
uv run --env-file .env.test pytest src/ecommerce_backoffice/domain/user

# Infrastructure level (needs the test database running)
uv run --env-file .env.test pytest src/ecommerce_backoffice/infrastructure/user

# Everything
uv run --env-file .env.test pytest
```

The infrastructure tests create the tables before the run and drop them afterwards.
Run them with `.env.test` only, never with `.env`.
