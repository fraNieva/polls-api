# Project Patterns and Standards

This document details the specific implementation patterns used in the Polls API project.

## 📊 Enhanced API Pattern (GET Endpoints)
All GET endpoints returning lists must follow the standardized pagination and search pattern.

### 1. Pagination Utilities
Use `app/api/v1/utils/pagination.py`:
- `PaginationParams`: Dependency for page/size.
- `paginate_query()`: Complete workflow for filtering, searching, and sorting.

### 2. Search & Filtering
- Search: Use `field.ilike(f"%{search}%")`.
- Filtering: Support `is_active`, `owner_id`, `created_after`, etc.
- Sorting: Use `Enum` validation for sort options.

## 🛡️ Centralized Response Structure
Never inline large response definitions. Use `app/api/v1/responses/`:
- `common_responses.py`: 401, 422, 500 errors.
- `poll_responses.py`: Success and business error responses for polls.

Example:
```python
@router.post("/", responses=get_poll_create_responses())
def create_poll(...):
    ...
```

## 🔄 Smart Update Pattern (PUT Endpoints)
Implement change detection to optimize performance and logging.
1. Track `changes_made` and `changed_fields`.
2. Normalize strings (strip whitespace) before comparison.
3. Only `db.commit()` if `changes_made` is True.
4. Smart Duplicate Validation: Exclude the current resource ID from uniqueness checks.

## 🔐 Hybrid Public/Private System
- `is_public` (bool): Controls visibility.
- **Anonymous**: See only public polls.
- **Authenticated**: See public + own private polls.
- **GET /{poll_id}**: Use `get_current_user_optional` to handle conditional access.

## 🧪 Testing Standards
- **Mocking**: Use `unittest.mock` for DB and external dependencies.
- **Coverage**: Maintain >85% coverage.
- **Scenario Focus**: Test success, validation errors, auth failures, and edge cases (e.g., max limits).

## 📝 Coding Style
- **Type Hints**: Mandatory for all function signatures.
- **Constants**: Always use `app.core.constants` for limits and error messages.
- **Docstrings**: Provide clear descriptions for models, schemas, and endpoints.
