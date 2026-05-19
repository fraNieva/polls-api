# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run the dev server
uvicorn main:app --reload

# Run all tests with coverage
pytest

# Run a single test file
pytest tests/test_polls.py -v

# Run a single test
pytest tests/test_polls.py::TestPollCRUD::test_create_poll_exceeds_limit_returns_429 -v

# Run tests by marker
pytest -m auth
pytest -m polls

# Initialize DB with sample data
python migration.db.py
```

Coverage target is ≥80% (fails under that). Reports go to `htmlcov/`.

## Architecture

Entry point is `main.py` at the repository root (not `app/main.py`). It creates the FastAPI app, registers CORS middleware, wires up four global exception handlers, and mounts all routers under `/api/v1`.

```
app/
  api/v1/
    endpoints/       # polls.py, users.py, auth.py, websocket.py
    responses/       # OpenAPI response definition factories
    utils/           # pagination.py — PaginationParams, paginate_query(), apply_search()
  core/
    constants.py     # ErrorMessages, BusinessLimits, ErrorCodes, APIConfig
    security.py      # JWT helpers (create_access_token, verify_token)
    exception.py     # Global exception handlers
    websocket_manager.py  # ConnectionManager singleton (manager)
  db/
    database.py      # SQLAlchemy engine + session factory
  models/            # SQLAlchemy ORM models: User, Poll, PollOption, Vote
  schemas/           # Pydantic v2 request/response schemas; PaginatedResponse[T] in common.py
tests/
main.py
```

## Key Patterns

**List endpoints** must use `PaginationParams`, `paginate_query()`, and `apply_search()` from `app/api/v1/utils/pagination.py`. Filtering supports `is_active`, `is_public`, `owner_id`, `created_after`; sort options are validated via `PollSortOption` enum.

**PUT endpoints** implement change detection: strip whitespace, compare each field, set `changes_made` flag, track `changed_fields` list, only commit when something actually changed.

**Error responses** always raise `HTTPException` with `detail` as a structured dict — never a plain string:
```python
raise HTTPException(status_code=404, detail={
    "message": ErrorMessages.POLL_NOT_FOUND,
    "error_code": ErrorCodes.POLL_NOT_FOUND,
    "poll_id": poll_id,
})
```

**Response definitions** live in `app/api/v1/responses/` — never inline large response dicts in endpoint decorators.

**Business rule validation** calls `_validate_poll_business_rules(user, db, operation)` at the top of create/update endpoints, with stricter rate limits for create than update.

## Authentication

- `get_current_user` — requires valid JWT; use for all write operations.
- `get_current_user_optional` — returns `None` for anonymous; use for reads and public-poll access.
- **GET /polls**: anonymous sees only `is_public=True`; authenticated sees public + own private polls.
- **GET /polls/{id}**: public polls open to anyone; private polls: 403 for authenticated non-owners, 401 for anonymous.

## WebSocket Broadcasting

`ConnectionManager` singleton in `app/core/websocket_manager.py` tracks `Dict[int, List[WebSocket]]` keyed by `poll_id`. After a vote is committed, `polls.py` reloads the poll, computes percentages, and broadcasts:

```python
anyio.from_thread.run(manager.broadcast_to_poll, poll_id, {"type": "vote_update", "data": poll_data})
```

Broadcast failures are caught and logged — they never roll back a valid vote. `user_has_voted` and `user_vote_option_id` are always `False`/`None` in the broadcast payload; clients track their own voting context locally.

## Coding Standards

- **Type hints** are mandatory on every function signature.
- **Constants only** from `app.core.constants` — never hardcode limits, messages, or error codes.
- **Logging**: `logging.getLogger(__name__)`; use `logger.exception()` inside `except` blocks.
- **Schemas**: Pydantic v2 only — `model_config = ConfigDict(...)`, never `class Config`. Use `model_dump(exclude_unset=True)` for partial updates.
- **Poll options**: max `BusinessLimits.MAX_POLL_OPTIONS` (10); duplicate check is case-insensitive; check current DB count before inserting.
- **Import order**: stdlib → third-party → local, separated by blank lines.
- **Docstrings**: required on models, schemas, and endpoint functions.
- **Commit messages**: Conventional Commits (`feat`, `fix`, `refactor`, `docs`, `test`, `chore`).

## Testing Conventions

- DB fixture `db_session` uses an in-memory SQLite instance; `mock_db_session` mocks the session for API-layer tests.
- Organize tests in classes per feature: `TestPollCRUD`, `TestPollPrivacy`, `TestVoting`, etc.
- Test names must describe the scenario: `test_create_poll_exceeds_limit_returns_429`.
- Cover: success path, validation errors, auth failures, duplicate/limit edge cases.
