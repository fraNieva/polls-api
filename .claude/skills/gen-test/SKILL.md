---
name: gen-test
description: Generate pytest tests for a FastAPI endpoint or module following project conventions
---

Generate tests in the project's established style:

1. Read `tests/conftest.py` to understand available fixtures
2. Read an existing test file for the same domain (e.g., test_poll_endpoints.py for polls)
3. Create a test class named `Test<Feature>` with methods named `test_<scenario_description>`
4. Use `db_session` for DB-layer tests, `mock_db_session` + `client` for API-layer tests
5. Cover: success path, validation errors, auth failures (401/403), business-rule limits (429)
6. Use constants from `app.core.constants` for expected messages and codes — never hardcode strings

Usage: /gen-test <module or endpoint to test>
