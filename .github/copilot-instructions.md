# GitHub Copilot Instructions — Polls API

This file is automatically loaded by VS Code Copilot as persistent project context.

---

## Project Overview

A production-ready **FastAPI** polling application with JWT authentication, paginated REST endpoints, atomic voting, and real-time WebSocket broadcasting.

| Concern | Choice |
|---|---|
| Framework | FastAPI 0.120.1 |
| ORM | SQLAlchemy 2.x |
| Database | SQLite (dev) / PostgreSQL (prod-ready) |
| Validation | Pydantic v2 |
| Auth | JWT via python-jose + bcrypt |
| Real-time | WebSocket (FastAPI native) + anyio |
| Testing | pytest + pytest-cov (~85 % coverage, 148 tests) |
| Python | 3.9+ |

Entry point: `main.py` (repository root, **not** `app/main.py`).

---

## Implemented Features

- Full Poll CRUD with smart change detection on PUT.
- Public / private visibility with hybrid auth (`get_current_user_optional`).
- Atomic voting with per-user duplicate prevention and daily limits.
- Dynamic poll option management (max 10 options, case-insensitive duplicate check).
- Server-side percentage calculation on every response.
- Centralized pagination, filtering, sorting, and search on all list endpoints.
- Standardized OpenAPI response definitions.
- Business rule validation: poll creation/update rate limiting, per-user poll limits.
- **Real-time WebSocket broadcasting**: when a vote is recorded, the updated
  poll is pushed to all connected clients on that poll's channel.

---

## Key Directories

```
app/
  api/v1/
    endpoints/       # One module per resource: polls.py, users.py, auth.py, websocket.py
    responses/       # Centralised OpenAPI response definitions
    utils/           # Reusable helpers: pagination.py
  core/
    constants.py     # ErrorMessages, BusinessLimits, ErrorCodes, APIConfig
    security.py      # JWT helpers
    exception.py     # Global exception handlers
    websocket_manager.py  # ConnectionManager singleton
  db/
    database.py      # SQLAlchemy engine + session factory
  models/            # SQLAlchemy ORM models
  schemas/           # Pydantic request / response schemas
tests/               # pytest test suite
main.py              # App factory, router registration, CORS, exception handlers
```

---

## Architecture & Patterns

### REST Endpoints
- **GET list endpoints** must use `app/api/v1/utils/pagination.py`:
  `PaginationParams`, `paginate_query()`, `apply_search()`.
- **Filtering**: `is_active`, `is_public`, `owner_id`, `created_after`.
  Use `Enum` for validated sort options (`PollSortOption`).
- **Responses**: never inline large response dicts — use the factories in
  `app/api/v1/responses/`.
- **PUT endpoints**: implement change detection (`changes_made` flag, strip
  whitespace before comparison, track `changed_fields` list, only commit when
  something changed; log specific fields changed vs. "no changes" branch).
- **Error handling**: raise `HTTPException` with structured `detail` dicts.
  Use constants from `app.core.constants` for all messages and codes.
- **Business rules**: call `_validate_poll_business_rules(user, db, operation)`
  at the start of create/update endpoints. Use different rate limits per
  operation type (stricter for create, more lenient for update).

### Authentication & Access Control
- `get_current_user` — requires a valid JWT; use for write operations.
- `get_current_user_optional` — returns `None` for anonymous; use for reads
  and public-poll access.
- Token is a Bearer JWT in the `Authorization` header.
- **Privacy filtering on GET /polls**: anonymous users see only `is_public=True`
  polls; authenticated users see public polls + their own private polls.
- **Privacy filtering on GET /polls/{id}**: public polls accessible to anyone;
  private polls accessible to owner only (403 for authenticated non-owners,
  401 for anonymous).

### Poll Options
- Max options per poll: `BusinessLimits.MAX_POLL_OPTIONS` (10).
- Max option text length: `BusinessLimits.MAX_POLL_OPTION_LENGTH` (200).
- Duplicate detection: case-insensitive text comparison before inserting.
- Options cannot be added to inactive polls.
- Always check current option count from DB before inserting.

### Schemas (Pydantic v2)
- All schemas use `model_dump(exclude_unset=True)` for partial updates.
- No deprecated v1 `class Config` — use `model_config = ConfigDict(...)`.
- Use `Field(...)` for required fields, `Field(None)` for optional.
- Generic paginated responses: `PaginatedResponse[T]` from `app/schemas/common.py`.

### WebSocket — Real-time Vote Broadcasting

**Endpoint**: `GET /api/v1/ws/polls/{poll_id}` (upgraded to WebSocket)

**`app/core/websocket_manager.py`** — `ConnectionManager` singleton (`manager`):
- `active_connections: Dict[int, List[WebSocket]]` — keyed by poll_id.
- `await manager.connect(ws, poll_id)` — accepts handshake and registers socket.
- `manager.disconnect(ws, poll_id)` — removes socket; deletes key when list empties.
- `await manager.broadcast_to_poll(poll_id, message: dict)` — sends JSON to all
  listeners; stale sockets are collected after the loop and removed via
  `disconnect()` to avoid mutating the list mid-iteration.

**`app/api/v1/endpoints/websocket.py`** — keeps connection alive:
```python
while True:
    await websocket.receive_text()   # detects client close / pings
```
Cleans up on `WebSocketDisconnect` or any unhandled exception.

**Vote broadcast in `vote_poll` (`polls.py`)**:
After `db.commit()`, the endpoint reloads the poll with options, computes
percentages, then calls:
```python
anyio.from_thread.run(
    manager.broadcast_to_poll,
    poll_id,
    {"type": "vote_update", "data": poll_data},
)
```
`user_has_voted` and `user_vote_option_id` are always `False`/`None` in the
broadcast — each client preserves its own voting context in its Redux store.
Broadcast failures are caught and logged; they never roll back a valid vote.

**Message contract sent to clients**:
```json
{
  "type": "vote_update",
  "data": {
    "id": 10,
    "title": "...",
    "options": [{"id": 1, "text": "...", "vote_count": 5, "percentage": 62.5}],
    "total_votes": 8,
    "user_has_voted": false,
    "user_vote_option_id": null
  }
}
```

---

## Coding Standards

- **Type hints** are mandatory on every function signature.
- **Constants**: use `app.core.constants` — never hardcode limits or error strings.
- **Logging**: use `logging.getLogger(__name__)`; use `logger.exception()` inside
  `except` blocks (not `logger.error(..., exc_info=True)`).
- **Docstrings**: required on models, schemas, and endpoints.
- **No print()** in production paths — use structured logging.
- **Import order**: stdlib → third-party → local; group with blank lines.
- **Error responses**: always include `detail` as a dict with `message`, `error_code`,
  and relevant context keys (e.g., `poll_id`, `owner_id`). Never return plain strings.

---

## Testing

- Framework: `pytest` with `pytest-cov`.
- Run: `pytest` from repository root (venv must be active).
- Coverage target: ≥ 85 %.
- Mock DB and external dependencies via `unittest.mock`.
- Cover: success, validation errors, auth failures, duplicate/limit edge cases.
- Organize tests in classes per feature: `TestPollCRUD`, `TestPollPrivacy`,
  `TestPollOptions`, `TestVoting`, etc.
- Test names must describe the scenario: `test_create_poll_exceeds_limit_returns_429`.

---

## Development Workflow

1. Check `app/models/` and `app/schemas/` before adding a new endpoint.
2. Follow the patterns above — pagination, response factories, change detection.
3. Add tests alongside new code.
4. Run `pytest` before committing.
5. Commit messages follow Conventional Commits: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`.

---

## Roadmap

1. ~~Real-time WebSocket vote broadcasting~~ ✅ Done
2. Analytics dashboard — poll performance metrics.
3. Categories and tags for poll discovery.
4. Poll templates (Yes/No, Rating scale, etc.).
5. Rate limiting, Redis caching, database indexing.
