# Technical Quiz: ecommerce_backoffice API

Mock-interview questions based on this repository. Answer each one out loud or in writing first,
then open the answer notes to compare. The notes list what a good answer covers; they are not the only valid wording.

- **Junior** (10): FastAPI basics, Python basics, what the code does.
- **Mid-level** (10): why the code is designed this way, transactions, testing.
- **Senior** (10): trade-offs, concurrency, scaling, what you would change in production.

Paths are relative to `src/ecommerce_backoffice/`.

---

## Junior

### J1. What is served at `/docs`, and where does the information come from?

`main.py` only creates `FastAPI()` and includes a router. You never wrote the Swagger page.

<details>
<summary>Answer notes</summary>

FastAPI builds an OpenAPI schema from the route decorators, the type hints of the endpoint parameters,
and the Pydantic models (`CreateUserRequest`, `UserResponse`). Swagger UI renders that schema.
`/openapi.json` is the raw schema.

</details>

### J2. In `controller/user_controller.py`, how does FastAPI know `user_id` is a path parameter and not a query parameter?

What happens for `GET /users/abc`?

<details>
<summary>Answer notes</summary>

`{user_id}` appears in the route path, so the function parameter with that name is read from the path.
A parameter not in the path is a query parameter (or the body, if it is a Pydantic model).
`user_id: UUID` makes FastAPI validate and convert it; `abc` is not a UUID, so the response is 422 before your code runs.

</details>

### J3. What does `BaseModel` give `CreateUserRequest` that a plain `@dataclass` does not?

<details>
<summary>Answer notes</summary>

Validation and type coercion at construction time (for example `"1990-01-01"` becomes `date`),
a `ValidationError` for missing or wrong-typed fields, and JSON (de)serialization.
A dataclass only generates `__init__`, `__repr__` and `__eq__` and does not check types.

</details>

### J4. Why does `POST /users` return 201 and `DELETE /users/{id}` return 204?

What error did FastAPI raise when `DELETE` had both `status_code=204` and a `response_model`?

<details>
<summary>Answer notes</summary>

201 means "created", 204 means "success, no content". HTTP forbids a body on 204, so FastAPI asserts
`Status code 204 must not have a response body` at startup if you declare a `response_model` for it.

</details>

### J5. What does `Depends(get_repo)` do for the endpoint?

<details>
<summary>Answer notes</summary>

FastAPI calls `get_repo` for each request and passes its return value into the parameter (dependency injection).
Dependencies can depend on other dependencies: `get_repo` itself depends on `get_session`.
The endpoint does not create the session or repository by itself, which makes it easy to replace in tests with `dependency_overrides`.

</details>

### J6. `Email` is `@dataclass(frozen=True)`. What does `frozen=True` change, and why is it a good fit for a value object?

<details>
<summary>Answer notes</summary>

Assigning to a field raises `FrozenInstanceError`, so the object is immutable, and `__hash__` is generated.
A value object is defined by its value (two `Email("a@b.co")` are equal) and must not change after it passed validation in `__post_init__`.

</details>

### J7. In `User`, why are `age` and `fullname` declared with `field(init=False)`?

<details>
<summary>Answer notes</summary>

They are derived values. `init=False` removes them from the generated `__init__`, so callers cannot pass inconsistent values;
`__post_init__` computes them from `date_of_birth`, `firstname`, `middlename` and `lastname`.

</details>

### J8. Explain `@pytest.mark.parametrize` and `pytest.raises` using `controller/dto/__test__/user_dto_test.py`.

<details>
<summary>Answer notes</summary>

`parametrize` runs one test function once per value, each as its own test case, so one failing value does not hide the others.
`pytest.raises(X)` is the assertion: the test passes only if the block raises `X`; no exception fails with `DID NOT RAISE`.

</details>

### J9. What does `CreateUserRequest(**VALID)` mean, and why did `CreateUserRequest(**VALID, date_of_birth=...)` fail?

<details>
<summary>Answer notes</summary>

`**` unpacks a dict into keyword arguments. `VALID` already contains `date_of_birth`, so passing it again gives
`TypeError: got multiple values for keyword argument`. Merge dicts with `VALID | overrides` instead.

</details>

### J10. Why does the app read the database credentials from environment variables, and what does `uv run --env-file .env` do?

<details>
<summary>Answer notes</summary>

Secrets and environment-specific values do not belong in source control; the same code runs with different values in dev, test and prod.
`uv` does not load `.env` by itself; `--env-file` loads the file into the process environment before the command runs.
`config.py` then reads them with `os.environ[...]`, so a missing variable fails fast with `KeyError`.

</details>

---

## Mid-level

### M1. Describe the architecture using this repo. Which layer may import which?

Where does `UserRepositoryPort` live, and why not next to `UserRepository`?

<details>
<summary>Answer notes</summary>

Dependencies point inward: controller → usecase → domain; infrastructure → domain (it implements the port).
The domain and usecases never import FastAPI, Pydantic or SQLAlchemy.
The port lives in the domain because the domain defines what it needs; infrastructure adapts to it (dependency inversion).
The composition root (`get_repo` in the controller) is where concrete classes are wired together.

</details>

### M2. Why are there both `User` (domain) and `UserRow` (ORM)? What does it cost?

<details>
<summary>Answer notes</summary>

It keeps the domain free of the persistence framework, so the ORM or database can change without touching business rules,
and domain rules do not depend on column types.
Cost: a mapping layer (`_to_row`, `_to_entity`) that must be kept in sync, and extra tests for it.

</details>

### M3. The repository calls `flush()`, not `commit()`. Who owns the transaction and why?

<details>
<summary>Answer notes</summary>

`get_session` owns it (`Session(engine)` + `session.begin()`): commit on success, rollback on exception.
`flush()` sends the SQL so constraint errors surface immediately, but the transaction stays open.
If each repository committed by itself, one use case touching two repositories could be half-saved.

</details>

### M4. Walk through one request through `get_session`. When is a connection taken from the pool, and when are commit and rollback decided?

<details>
<summary>Answer notes</summary>

`Session(engine)` does not connect yet. The connection is checked out from the pool on the first SQL (here the first `flush()` or `get`).
When the dependency exits without an exception the transaction commits; with an exception it rolls back and the exception propagates.
The connection returns to the pool when the session closes.

</details>

### M5. Why does `get_repo` use `Depends(get_session, scope="function")`?

<details>
<summary>Answer notes</summary>

For a dependency with `yield`, `scope="function"` runs the code after `yield` (the commit) before the response is sent;
the default `"request"` runs it after the response is sent.
With the default, a failed commit would happen after the client already received `201`. This was checked against the installed FastAPI version.

</details>

### M6. Where should validation live: the DTO or the domain? Why is the email format checked in `Email`, not in `CreateUserRequest`?

How does an invalid email become a 422?

<details>
<summary>Answer notes</summary>

The DTO validates shape (required fields, types). Business rules (email format, age >= 18, non-blank names) belong to the domain so every entry point shares them.
`Email.__post_init__` raises `InvalidUserError`; the exception handler in `main.py` turns it into 422 with `field` and `reason`.
The handler lives at app level so no endpoint needs its own `try/except`.

</details>

### M7. `POST /users` with an existing email returns 500. Why, and how would you fix it properly?

<details>
<summary>Answer notes</summary>

The unique constraint raises SQLAlchemy `IntegrityError` at `flush()`, and nothing maps it, so it becomes an unhandled 500.
Fix: the adapter catches `IntegrityError` and raises a domain/port error (for example `DuplicatedUserError`), and a handler returns 409.
Do not rely on a "select then insert" pre-check alone: two requests can pass the check at the same time, so the DB constraint stays the source of truth.

</details>

### M8. `test_save_then_find` may not read from the database at all. Why?

<details>
<summary>Answer notes</summary>

`Session.get` checks the identity map first, and the `UserRow` just added is still in the same session, so it can return it without a `SELECT`.
To force a real read, call `session.expire_all()` (or use a fresh session) before `find_one_by_id`.

</details>

### M9. Why test the repository against real Postgres, and what is dangerous about the current fixture?

<details>
<summary>Answer notes</summary>

Mocking the session only proves method calls; a real database proves SQL, constraints and type mapping.
Each test rolls back, which works because the repository only flushes.
Danger: the session fixture calls `drop_all`, and the test engine reads the same `DB_*` variables as the app,
so running tests with the dev `.env` would drop the dev tables. Mitigations: separate env file, a guard that refuses non-test database names.

</details>

### M10. What does `Base.metadata.create_all(engine)` in `main.py` do, and what does it not do?

<details>
<summary>Answer notes</summary>

It issues `CREATE TABLE` for tables that do not exist yet. It never alters existing tables (no new column, no type change), so schema changes need a migration tool such as Alembic.
Running it on every startup of several instances can also race.

</details>

---

## Senior

### S1. Two requests create the same email at the same moment. Walk through what happens and what guarantees correctness.

<details>
<summary>Answer notes</summary>

Both can pass any application-level check. The unique index makes the second insert fail (or wait for the first transaction to finish, then fail).
Correctness comes from the database constraint plus translating the error to a 409; transaction isolation level matters for read-then-write logic but not for a unique index.
Idempotency keys are the next step if clients retry `POST`.

</details>

### S2. The endpoints are plain `def` with a synchronous `Session`. How does FastAPI run them, and when would you move to async?

What would change in the port and the adapter?

<details>
<summary>Answer notes</summary>

Sync endpoints run in a thread pool (default about 40 threads), so blocking DB calls do not block the event loop but concurrency is limited by threads and pool size.
Moving to `AsyncSession` and an async driver makes the port methods `async def`, which ripples into the usecases and tests.
Hexagonal design confines the change to the port, usecases, adapter and composition root; the domain stays untouched.

</details>

### S3. Size the connection pool for this service. What can go wrong under load?

<details>
<summary>Answer notes</summary>

SQLAlchemy's default pool is 5 connections plus 10 overflow per process; each uvicorn worker has its own pool.
Total connections = workers x (pool_size + max_overflow) must stay under Postgres `max_connections` (or use PgBouncer).
Too small a pool makes requests wait and time out; too large exhausts Postgres.
Consider `pool_pre_ping` for stale connections and `pool_timeout` to fail fast.

</details>

### S4. Design login and logout with a password and JWT. Which ports, which layers?

`sigin.py` and `signout.py` are empty today.

<details>
<summary>Answer notes</summary>

Store only a password hash (argon2 or bcrypt) in `UserRow` and the entity, never in responses.
Add `PasswordHasherPort` and `TokenIssuerPort` in the domain, with adapters in infrastructure; the signin usecase verifies the hash and issues a token;
a FastAPI dependency verifies the token on each request.
Logout with stateless JWT needs short expiry plus refresh tokens, or a denylist/session table if immediate revocation is required.
Keep secrets and expiry in configuration, and use constant-time comparison.

</details>

### S5. After creating a user you must send a welcome email. Where does it go, and what can fail?

<details>
<summary>Answer notes</summary>

Sending inside the request couples latency and failure to the mail provider, and the DB write and the email cannot be one atomic operation (dual-write problem).
Use the outbox pattern: write an event row in the same transaction, and a separate worker sends it with retries.
Put a `Notifier` port behind the usecase; keep sending idempotent.

</details>

### S6. `_to_entity` builds `User` through `__post_init__`. What are the consequences when loading old rows?

<details>
<summary>Answer notes</summary>

Loading re-runs validation, so a rule change (for example `MIN_AGE` raised) can make existing users impossible to load,
and `create_date` is overwritten by `datetime.now()` and has to be reassigned by hand.
Cleaner: separate creation (with rules) from reconstitution (trusting stored state), for example a factory or classmethod for each.

</details>

### S7. Usecases return the `User` entity. When is that wrong, and how do you stop leaking fields such as `password_hash`?

<details>
<summary>Answer notes</summary>

Returning the entity is fine while a controller maps it to a response model, as `UserResponse.from_entity` does.
It becomes wrong when a usecase assembles data from several aggregates or serves several delivery mechanisms: return an output DTO.
Never serialize the entity directly; use an explicit `response_model` with only the allowed fields, and add a test asserting the exact response keys.

</details>

### S8. How do you evolve the schema with zero downtime while old and new app versions run together?

<details>
<summary>Answer notes</summary>

Expand and contract: add the new nullable column or table first, deploy code that writes both, backfill, switch reads, then remove the old column in a later release.
Use Alembic migrations run once in CI/CD, not `create_all` at app startup, and make each step backward compatible.
Avoid long locks (for example create indexes concurrently).

</details>

### S9. Design the error contract and observability for this API.

<details>
<summary>Answer notes</summary>

One consistent error body (code, field, message), domain errors mapped centrally in exception handlers (422 validation, 404 missing, 409 conflict, 500 unexpected).
Do not echo sensitive input back (the handler already leaves out `exc.value`).
Add a request id, structured logs, metrics and tracing; log unexpected errors with the traceback server-side only.

</details>

### S10. How do you prove any new adapter (in-memory, MySQL, async) honours `UserRepositoryPort`?

How would you test endpoints without a database?

<details>
<summary>Answer notes</summary>

Write one contract test suite for the port (save then find, delete, missing, duplicate) and run it against every adapter.
For endpoints, use `app.dependency_overrides` with an in-memory fake repository and `TestClient`.
Keep a small number of real-database tests (for example via a container in CI) for SQL behaviour, constraints and migrations.

</details>
