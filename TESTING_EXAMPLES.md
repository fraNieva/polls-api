# Testing Enhanced Authentication - Examples

## Test the Enhanced GET /polls/{poll_id} Endpoint

### 1. **Test Anonymous Access (No Authentication)**

```bash
# Should work - returns poll data
curl -X GET "http://localhost:8000/api/v1/polls/1" \
  -H "Content-Type: application/json"
```

### 2. **Test Authenticated Access**

```bash
# First, get a token
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'

# Use the token (replace YOUR_TOKEN with actual token)
curl -X GET "http://localhost:8000/api/v1/polls/1" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 3. **Test Invalid Poll ID (Enhanced Validation)**

```bash
# Should return 422 with structured error
curl -X GET "http://localhost:8000/api/v1/polls/0" \
  -H "Content-Type: application/json"

# Expected response:
{
  "detail": {
    "message": "Validation failed",
    "error_code": "VALIDATION_ERROR",
    "errors": [
      {
        "loc": ["path", "poll_id"],
        "msg": "Poll ID must be greater than 0",
        "type": "value_error.number.not_gt",
        "ctx": {"limit_value": 0}
      }
    ],
    "poll_id": 0
  }
}
```

### 4. **Test Non-existent Poll**

```bash
# Should return 404 with structured error
curl -X GET "http://localhost:8000/api/v1/polls/999999" \
  -H "Content-Type: application/json"

# Expected response:
{
  "detail": {
    "message": "Poll not found",
    "error_code": "POLL_NOT_FOUND",
    "poll_id": 999999
  }
}
```

## Future Testing (When is_public field is added)

### 5. **Test Private Poll Access (Anonymous) - Future**

```bash
# Should return 401 when accessing private poll without auth
curl -X GET "http://localhost:8000/api/v1/polls/2" \
  -H "Content-Type: application/json"

# Expected future response:
{
  "detail": {
    "message": "Authentication required to access this private poll",
    "error_code": "AUTHENTICATION_REQUIRED",
    "poll_id": 2
  }
}
```

### 6. **Test Private Poll Access (Wrong User) - Future**

```bash
# Should return 403 when authenticated user tries to access someone else's private poll
curl -X GET "http://localhost:8000/api/v1/polls/2" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Expected future response:
{
  "detail": {
    "message": "Access denied to this private poll",
    "error_code": "ACCESS_DENIED",
    "poll_id": 2,
    "owner_id": 5
  }
}
```

## Check Enhanced API Documentation

### 7. **View OpenAPI Documentation**

```bash
# Open in browser
open http://localhost:8000/docs

# Or check the JSON schema
curl -X GET "http://localhost:8000/openapi.json"
```

The enhanced GET endpoint now shows:

- ✅ 200: Successful poll retrieval
- ✅ 401: Authentication required (for future private polls)
- ✅ 403: Access denied (for future private polls)
- ✅ 404: Poll not found
- ✅ 422: Validation error
- ✅ 500: Server error

## Run Tests to Verify Everything Works

```bash
# Test the enhanced endpoint specifically
python -m pytest tests/test_poll_endpoints.py::TestPollRetrieval::test_get_poll_by_id -v

# Test all poll retrieval functionality
python -m pytest tests/test_poll_endpoints.py::TestPollRetrieval -v

# Run all tests to ensure no regression
python -m pytest tests/test_poll_endpoints.py -v
```

## Check Logs for Authentication Status

The enhanced endpoint now logs:

- ✅ Authentication status (authenticated/anonymous)
- ✅ User information (user ID or "anonymous user")
- ✅ Poll access attempts with context
- ✅ Enhanced error details

Example log entries:

```
INFO: Retrieving poll ID 1 by user 123 (authenticated)
INFO: Retrieving poll ID 1 by anonymous user (anonymous)
WARN: Invalid poll ID provided: 0
WARN: Poll not found: ID 999999
```
