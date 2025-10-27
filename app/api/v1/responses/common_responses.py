"""
Common reusable response definitions for FastAPI endpoints.

This module contains response configurations that are shared across multiple endpoints,
promoting consistency and reducing duplication in OpenAPI documentation.
"""

from app.schemas.error import (
    ValidationErrorResponse,
    BusinessErrorResponse, 
    AuthErrorResponse,
    RateLimitErrorResponse,
    ServerErrorResponse
)

# Constants for common values
CONTENT_TYPE_JSON = "application/json"
EXAMPLE_TIMESTAMP = "2024-01-01T12:00:00Z"
EXAMPLE_API_PATH = "/api/v1/endpoint"
VALIDATION_FAILED_MESSAGE = "Validation failed"
VALIDATION_ERROR_CODE = "VALIDATION_ERROR"


# Common authentication error response
AUTH_ERROR_RESPONSE = {
    "description": "Authentication required",
    "model": AuthErrorResponse,
    "content": {
        CONTENT_TYPE_JSON: {
            "example": {
                "message": "Authentication required",
                "error_code": "AUTHENTICATION_REQUIRED",
                "timestamp": EXAMPLE_TIMESTAMP,
                "path": EXAMPLE_API_PATH
            }
        }
    }
}

# Common validation error response with reusable examples
def get_validation_error_response(path: str = EXAMPLE_API_PATH):
    """Generate validation error response with context-specific path."""
    return {
        "description": "Validation error",
        "model": ValidationErrorResponse,
        "content": {
            CONTENT_TYPE_JSON: {
                "examples": {
                    "invalid_page": {
                        "summary": "Invalid page parameter",
                        "value": {
                            "message": VALIDATION_FAILED_MESSAGE,
                            "error_code": VALIDATION_ERROR_CODE,
                            "errors": [
                                {
                                    "loc": ["query", "page"],
                                    "msg": "ensure this value is greater than 0",
                                    "type": "value_error.number.not_gt",
                                    "ctx": {"limit_value": 0}
                                }
                            ],
                            "timestamp": EXAMPLE_TIMESTAMP,
                            "path": path
                        }
                    },
                    "invalid_size": {
                        "summary": "Invalid page size parameter",
                        "value": {
                            "message": VALIDATION_FAILED_MESSAGE,
                            "error_code": VALIDATION_ERROR_CODE,
                            "errors": [
                                {
                                    "loc": ["query", "size"],
                                    "msg": "ensure this value is less than or equal to 100",
                                    "type": "value_error.number.not_le",
                                    "ctx": {"limit_value": 100}
                                }
                            ],
                            "timestamp": EXAMPLE_TIMESTAMP,
                            "path": path
                        }
                    },
                    "invalid_sort": {
                        "summary": "Invalid sort parameter",
                        "value": {
                            "message": VALIDATION_FAILED_MESSAGE,
                            "error_code": VALIDATION_ERROR_CODE,
                            "errors": [
                                {
                                    "loc": ["query", "sort"],
                                    "msg": "value is not a valid enumeration member",
                                    "type": "type_error.enum",
                                    "ctx": {"enum_values": ["created_desc", "created_asc", "title_asc", "title_desc", "votes_desc", "votes_asc"]}
                                }
                            ],
                            "timestamp": EXAMPLE_TIMESTAMP,
                            "path": path
                        }
                    }
                }
            }
        }
    }

# Common rate limit error response
RATE_LIMIT_ERROR_RESPONSE = {
    "description": "Rate limit exceeded", 
    "model": RateLimitErrorResponse,
    "content": {
        CONTENT_TYPE_JSON: {
            "example": {
                "message": "Rate limit exceeded",
                "error_code": "RATE_LIMIT_EXCEEDED",
                "retry_after": "3600",
                "timestamp": EXAMPLE_TIMESTAMP,
                "path": EXAMPLE_API_PATH
            }
        }
    }
}

# Common server error response
def get_server_error_response(error_code: str = "INTERNAL_ERROR", path: str = EXAMPLE_API_PATH):
    """Generate server error response with context-specific error code and path."""
    return {
        "description": "Internal server error",
        "model": ServerErrorResponse,
        "content": {
            CONTENT_TYPE_JSON: {
                "example": {
                    "message": "An unexpected error occurred",
                    "error_code": error_code,
                    "timestamp": EXAMPLE_TIMESTAMP,
                    "path": path
                }
            }
        }
    }

# Shorthand references for common responses
VALIDATION_ERROR_RESPONSE = get_validation_error_response()
SERVER_ERROR_RESPONSE = get_server_error_response()

# Common validation examples for query parameters
common_validation_examples = {
    "invalid_page": {
        "summary": "Invalid page parameter",
        "value": {
            "message": VALIDATION_FAILED_MESSAGE,
            "error_code": VALIDATION_ERROR_CODE,
            "errors": [
                {
                    "loc": ["query", "page"],
                    "msg": "ensure this value is greater than 0",
                    "type": "value_error.number.not_gt",
                    "ctx": {"limit_value": 0}
                }
            ],
            "timestamp": EXAMPLE_TIMESTAMP
        }
    },
    "invalid_size": {
        "summary": "Invalid page size parameter", 
        "value": {
            "message": VALIDATION_FAILED_MESSAGE,
            "error_code": VALIDATION_ERROR_CODE,
            "errors": [
                {
                    "loc": ["query", "size"],
                    "msg": "ensure this value is less than or equal to 100",
                    "type": "value_error.number.not_le",
                    "ctx": {"limit_value": 100}
                }
            ],
            "timestamp": EXAMPLE_TIMESTAMP
        }
    }
}

# Common server error example
common_server_error_example = {
    "message": "An unexpected error occurred",
    "error_code": "INTERNAL_ERROR",
    "timestamp": EXAMPLE_TIMESTAMP
}