# Gemini Project Instructions - Polls API

This file contains the foundational mandates and guidance for Gemini CLI when working on the Polls API project.

## 🚀 Project Overview
A production-ready FastAPI-based polling application with comprehensive features, authentication, and extensive test coverage (~85%+).

- **Framework**: FastAPI 0.119.0 (Async support)
- **Database**: SQLAlchemy 2.0.44 (SQLite for dev, PostgreSQL for prod)
- **Validation**: Pydantic v2
- **Auth**: JWT with python-jose and bcrypt

## 🎯 Core Mandates
- **TDD First**: Write tests before implementation whenever possible.
- **Code Quality**: Maintain high-quality, production-ready code with comprehensive error handling.
- **Type Safety**: Rigorous use of type hints, Enums for validation, and Pydantic schemas.
- **API Consistency**: ALL GET endpoints must support pagination, filtering, sorting, and search.
- **Documentation**: Keep OpenAPI documentation complete with examples for all status codes.

## 🏗️ Architectural Patterns
- **Enhanced API Pattern**: Centralized pagination and search utilities in `app/api/v1/utils/pagination.py`.
- **Centralized Responses**: All endpoints must use response definitions from `app/api/v1/responses/`.
- **Smart Update Logic**: PUT endpoints should implement change detection to avoid unnecessary DB writes.
- **Hybrid Privacy**: Polls can be public (accessible to all) or private (owner-only).

## 🛠️ Development Workflow
1. **Research**: Analyze existing models in `app/models/` and schemas in `app/schemas/`.
2. **Standardization**: Ensure new endpoints follow the [Patterns and Standards](.gemini/patterns.md).
3. **Testing**: Add new test cases to `tests/` (e.g., `tests/test_poll_endpoints.py`).
4. **Validation**: Run `pytest` and ensure no regressions.

## 📚 Key Directories
- `app/api/v1/endpoints/`: Individual endpoint modules.
- `app/api/v1/responses/`: Centralized response definitions.
- `app/api/v1/utils/`: Reusable utilities (pagination, etc.).
- `app/core/`: Configuration, security, and constants.
- `app/models/`: SQLAlchemy database models.
- `app/schemas/`: Pydantic validation schemas.

---
*Refer to [.gemini/patterns.md](.gemini/patterns.md) for detailed implementation standards.*
