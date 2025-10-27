"""
Poll-specific response definitions for FastAPI endpoints.

This module contains response configurations specific to poll operations,
building upon common responses for maximum reusability.
"""

from app.schemas.poll import PollRead
from app.schemas.common import PaginatedResponse
from app.schemas.error import BusinessErrorResponse, ValidationErrorResponse, AuthErrorResponse
from .common_responses import (
    AUTH_ERROR_RESPONSE,
    get_validation_error_response,
    get_server_error_response,
    RATE_LIMIT_ERROR_RESPONSE,
    CONTENT_TYPE_JSON,
    EXAMPLE_TIMESTAMP
)

# Constants for poll paths
POLLS_BASE_PATH = "/api/v1/polls/"
MY_POLLS_PATH = "/api/v1/polls/my-polls"

# Poll success response examples
POLL_SUCCESS_EXAMPLE = {
    "id": 1,
    "title": "Favorite Programming Language",
    "description": "Vote for your preferred language",
    "is_active": True,
    "owner_id": 1,
    "pub_date": "2024-01-01T12:00:00Z",
    "options": []
}

POLL_WITH_OPTIONS_EXAMPLE = {
    "id": 1,
    "title": "My Programming Poll",
    "description": "A poll I created about programming languages",
    "is_active": True,
    "owner_id": 1,
    "pub_date": "2024-01-01T12:00:00Z",
    "options": [
        {
            "id": 1,
            "text": "Python",
            "vote_count": 5
        },
        {
            "id": 2,
            "text": "JavaScript",
            "vote_count": 3
        }
    ]
}

PAGINATED_POLLS_EXAMPLE = {
    "items": [POLL_SUCCESS_EXAMPLE],
    "total": 1,
    "page": 1,
    "size": 10,
    "pages": 1
}

PAGINATED_USER_POLLS_EXAMPLE = {
    "items": [POLL_WITH_OPTIONS_EXAMPLE],
    "total": 1,
    "page": 1,
    "size": 10,
    "pages": 1
}

# Poll-specific error responses
def get_poll_business_error_response(path: str):
    """Generate business logic error response for polls."""
    return {
        "description": "Business logic error",
        "model": BusinessErrorResponse,
        "content": {
            CONTENT_TYPE_JSON: {
                "examples": {
                    "duplicate_poll": {
                        "summary": "Duplicate poll title",
                        "value": {
                            "message": "A poll with this title already exists",
                            "error_code": "DUPLICATE_POLL_TITLE",
                            "details": {"existing_poll_id": 123},
                            "timestamp": EXAMPLE_TIMESTAMP,
                            "path": path
                        }
                    },
                    "poll_limit": {
                        "summary": "Poll creation limit exceeded",
                        "value": {
                            "message": "Maximum number of polls per user exceeded (100)",
                            "error_code": "POLL_LIMIT_EXCEEDED",
                            "details": {
                                "current_count": 100,
                                "max_allowed": 100
                            },
                            "timestamp": EXAMPLE_TIMESTAMP,
                            "path": path
                        }
                    },
                    "integrity_error": {
                        "summary": "Database integrity constraint violated",
                        "value": {
                            "message": "Data integrity constraint violated",
                            "error_code": "INTEGRITY_ERROR",
                            "hint": "Check for duplicate values or invalid references",
                            "timestamp": EXAMPLE_TIMESTAMP,
                            "path": path
                        }
                    }
                }
            }
        }
    }

def get_poll_not_found_response(path: str):
    """Generate poll not found error response."""
    return {
        "description": "Poll not found",
        "model": BusinessErrorResponse,
        "content": {
            CONTENT_TYPE_JSON: {
                "example": {
                    "message": "Poll not found",
                    "error_code": "POLL_NOT_FOUND",
                    "poll_id": 999,
                    "timestamp": EXAMPLE_TIMESTAMP,
                    "path": path
                }
            }
        }
    }

def get_poll_forbidden_response(path: str):
    """Generate poll access forbidden error response."""
    return {
        "description": "Access forbidden - not poll owner",
        "model": BusinessErrorResponse,
        "content": {
            CONTENT_TYPE_JSON: {
                "example": {
                    "message": "Not authorized to update this poll",
                    "error_code": "NOT_AUTHORIZED_UPDATE",
                    "poll_id": 1,
                    "owner_id": 2,
                    "timestamp": EXAMPLE_TIMESTAMP,
                    "path": path
                }
            }
        }
    }

def get_poll_validation_response(path: str):
    """Generate validation error response specific to polls."""
    base_response = get_validation_error_response(path)
    # Add poll-specific validation examples
    base_response["content"][CONTENT_TYPE_JSON]["examples"]["invalid_title"] = {
        "summary": "Invalid poll title",
        "value": {
            "message": "Validation failed",
            "error_code": "VALIDATION_ERROR",
            "errors": [
                {
                    "loc": ["title"],
                    "msg": "ensure this value has at least 5 characters",
                    "type": "value_error.any_str.min_length",
                    "ctx": {"limit_value": 5}
                }
            ],
            "timestamp": EXAMPLE_TIMESTAMP,
            "path": path
        }
    }
    return base_response

# Complete response sets for different poll endpoints

# Poll creation responses
POLL_CREATE_RESPONSES = {
    201: {
        "description": "Poll created successfully",
        "model": PollRead,
        "content": {
            CONTENT_TYPE_JSON: {
                "example": POLL_SUCCESS_EXAMPLE
            }
        }
    },
    401: AUTH_ERROR_RESPONSE,
    429: RATE_LIMIT_ERROR_RESPONSE
}

# Poll update responses
def get_poll_update_responses(poll_id: int = 1):
    """Generate complete response set for poll update endpoint."""
    path = f"/api/v1/polls/{poll_id}"
    return {
        200: {
            "description": "Poll updated successfully",
            "model": PollRead,
            "content": {
                CONTENT_TYPE_JSON: {
                    "example": {
                        **POLL_SUCCESS_EXAMPLE,
                        "title": "Updated Poll Title",
                        "description": "Updated description"
                    }
                }
            }
        },
        400: get_poll_business_error_response(path),
        401: AUTH_ERROR_RESPONSE,
        403: get_poll_forbidden_response(path),
        404: get_poll_not_found_response(path),
        422: get_poll_validation_response(path),
        500: get_server_error_response("INTERNAL_ERROR", path)
    }

# Poll list responses  
def get_poll_list_responses(path: str = POLLS_BASE_PATH):
    """Generate complete response set for poll list endpoint."""
    return {
        200: {
            "description": "Polls retrieved successfully",
            "model": PaginatedResponse[PollRead],
            "content": {
                CONTENT_TYPE_JSON: {
                    "example": PAGINATED_POLLS_EXAMPLE
                }
            }
        },
        422: get_validation_error_response(path),
        500: get_server_error_response("POLL_RETRIEVAL_FAILED", path)
    }

# User polls responses
def get_user_polls_responses(path: str = MY_POLLS_PATH):
    """Generate complete response set for user polls endpoint."""
    return {
        200: {
            "description": "User polls retrieved successfully",
            "model": PaginatedResponse[PollRead],
            "content": {
                CONTENT_TYPE_JSON: {
                    "example": PAGINATED_USER_POLLS_EXAMPLE
                }
            }
        },
        401: AUTH_ERROR_RESPONSE,
        422: get_validation_error_response(path),
        500: get_server_error_response("USER_POLLS_RETRIEVAL_FAILED", path)
    }

# Single poll by ID responses with optional authentication
def get_single_poll_responses(poll_id: int = 1):
    """Generate complete response set for single poll retrieval endpoint with optional authentication."""
    path = f"/api/v1/polls/{poll_id}"
    return {
        200: {
            "description": "Poll retrieved successfully",
            "model": PollRead,
            "content": {
                CONTENT_TYPE_JSON: {
                    "example": POLL_WITH_OPTIONS_EXAMPLE
                }
            }
        },
        401: {
            "description": "Authentication required for private poll access",
            "model": AuthErrorResponse,
            "content": {
                CONTENT_TYPE_JSON: {
                    "example": {
                        "message": "Authentication required to access this private poll",
                        "error_code": "AUTHENTICATION_REQUIRED",
                        "poll_id": poll_id,
                        "timestamp": EXAMPLE_TIMESTAMP,
                        "path": path
                    }
                }
            }
        },
        403: {
            "description": "Access denied to private poll",
            "model": BusinessErrorResponse,
            "content": {
                CONTENT_TYPE_JSON: {
                    "example": {
                        "message": "Access denied to this private poll",
                        "error_code": "ACCESS_DENIED",
                        "poll_id": poll_id,
                        "owner_id": 2,
                        "timestamp": EXAMPLE_TIMESTAMP,
                        "path": path
                    }
                }
            }
        },
        404: get_poll_not_found_response(path),
        422: {
            "description": "Validation error - invalid poll ID",
            "model": ValidationErrorResponse,
            "content": {
                CONTENT_TYPE_JSON: {
                    "example": {
                        "message": "Validation failed",
                        "error_code": "VALIDATION_ERROR",
                        "errors": [
                            {
                                "loc": ["path", "poll_id"],
                                "msg": "ensure this value is greater than 0",
                                "type": "value_error.number.not_gt",
                                "ctx": {"limit_value": 0}
                            }
                        ],
                        "timestamp": EXAMPLE_TIMESTAMP,
                        "path": path
                    }
                }
            }
        },
        500: get_server_error_response("POLL_RETRIEVAL_FAILED", path)
    }

# Poll creation responses with business logic errors
def get_poll_create_responses(path: str = POLLS_BASE_PATH):
    """Generate complete response set for poll creation endpoint."""
    return {
        **POLL_CREATE_RESPONSES,
        400: get_poll_business_error_response(path),
        422: get_poll_validation_response(path),
        500: get_server_error_response("INTERNAL_ERROR", path)
    }

# Poll deletion responses with comprehensive error handling
def get_poll_delete_responses(poll_id: int = 1):
    """Generate complete response set for poll deletion endpoint."""
    path = f"/api/v1/polls/{poll_id}"
    return {
        200: {
            "description": "Poll deleted successfully",
            "content": {
                CONTENT_TYPE_JSON: {
                    "example": {
                        "message": "Poll deleted successfully",
                        "poll_id": poll_id,
                        "timestamp": EXAMPLE_TIMESTAMP
                    }
                }
            }
        },
        401: AUTH_ERROR_RESPONSE,
        403: {
            "description": "Access forbidden - not poll owner",
            "model": BusinessErrorResponse,
            "content": {
                CONTENT_TYPE_JSON: {
                    "example": {
                        "message": "Not authorized to delete this poll",
                        "error_code": "NOT_AUTHORIZED_DELETE",
                        "poll_id": poll_id,
                        "owner_id": 2,
                        "timestamp": EXAMPLE_TIMESTAMP,
                        "path": path
                    }
                }
            }
        },
        404: get_poll_not_found_response(path),
        422: {
            "description": "Validation error - invalid poll ID",
            "model": ValidationErrorResponse,
            "content": {
                CONTENT_TYPE_JSON: {
                    "example": {
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
                        "poll_id": poll_id,
                        "timestamp": EXAMPLE_TIMESTAMP,
                        "path": path
                    }
                }
            }
        },
        500: get_server_error_response("POLL_DELETION_FAILED", path)
    }

# Convenience exports for common use cases
POLL_SUCCESS_RESPONSES = POLL_CREATE_RESPONSES
POLL_ERROR_RESPONSES = {
    400: get_poll_business_error_response(POLLS_BASE_PATH),
    401: AUTH_ERROR_RESPONSE,
    404: get_poll_not_found_response(POLLS_BASE_PATH),
    422: get_poll_validation_response(POLLS_BASE_PATH),
    500: get_server_error_response()
}

# =============================================================================
# Poll Option Response Definitions
# =============================================================================

def get_poll_option_create_responses(poll_id: int = 1):
    """Generate complete response set for poll option creation endpoint."""
    path = f"/api/v1/polls/{poll_id}/options"
    
    return {
        201: {
            "description": "Poll option created successfully",
            "content": {
                CONTENT_TYPE_JSON: {
                    "example": {
                        "message": "Poll option added successfully",
                        "option": {
                            "id": 123,
                            "text": "Python",
                            "vote_count": 0,
                            "poll_id": poll_id
                        },
                        "poll_id": poll_id,
                        "timestamp": EXAMPLE_TIMESTAMP
                    }
                }
            }
        },
        400: {
            "description": "Business logic error",
            "model": BusinessErrorResponse,
            "content": {
                CONTENT_TYPE_JSON: {
                    "examples": {
                        "duplicate_option": {
                            "summary": "Duplicate option text",
                            "value": {
                                "message": "An option with this text already exists for this poll",
                                "error_code": "DUPLICATE_POLL_OPTION",
                                "poll_id": poll_id,
                                "existing_option_text": "Python",
                                "timestamp": EXAMPLE_TIMESTAMP,
                                "path": path
                            }
                        },
                        "too_many_options": {
                            "summary": "Maximum options exceeded",
                            "value": {
                                "message": "Maximum number of options for this poll exceeded (10)",
                                "error_code": "MAX_OPTIONS_EXCEEDED",
                                "poll_id": poll_id,
                                "current_count": 10,
                                "max_allowed": 10,
                                "timestamp": EXAMPLE_TIMESTAMP,
                                "path": path
                            }
                        },
                        "poll_inactive": {
                            "summary": "Poll is not active",
                            "value": {
                                "message": "Cannot add options to an inactive poll",
                                "error_code": "POLL_INACTIVE",
                                "poll_id": poll_id,
                                "timestamp": EXAMPLE_TIMESTAMP,
                                "path": path
                            }
                        }
                    }
                }
            }
        },
        401: AUTH_ERROR_RESPONSE,
        403: {
            "description": "Access denied - not poll owner",
            "model": AuthErrorResponse,
            "content": {
                CONTENT_TYPE_JSON: {
                    "example": {
                        "message": "You can only add options to your own polls",
                        "error_code": "INSUFFICIENT_PERMISSIONS",
                        "poll_id": poll_id,
                        "owner_id": 2,
                        "timestamp": EXAMPLE_TIMESTAMP,
                        "path": path
                    }
                }
            }
        },
        404: get_poll_not_found_response(path),
        422: {
            "description": "Validation error",
            "model": ValidationErrorResponse,
            "content": {
                CONTENT_TYPE_JSON: {
                    "examples": {
                        "invalid_poll_id": {
                            "summary": "Invalid poll ID format",
                            "value": {
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
                                "poll_id": poll_id,
                                "timestamp": EXAMPLE_TIMESTAMP,
                                "path": path
                            }
                        },
                        "empty_option_text": {
                            "summary": "Empty option text",
                            "value": {
                                "message": "Validation failed",
                                "error_code": "VALIDATION_ERROR",
                                "errors": [
                                    {
                                        "loc": ["body", "text"],
                                        "msg": "Option text cannot be empty or just whitespace",
                                        "type": "value_error"
                                    }
                                ],
                                "poll_id": poll_id,
                                "timestamp": EXAMPLE_TIMESTAMP,
                                "path": path
                            }
                        },
                        "option_too_long": {
                            "summary": "Option text too long",
                            "value": {
                                "message": "Validation failed",
                                "error_code": "VALIDATION_ERROR",
                                "errors": [
                                    {
                                        "loc": ["body", "text"],
                                        "msg": "Option text must be at most 100 characters long",
                                        "type": "value_error.any_str.max_length",
                                        "ctx": {"limit_value": 100}
                                    }
                                ],
                                "poll_id": poll_id,
                                "timestamp": EXAMPLE_TIMESTAMP,
                                "path": path
                            }
                        }
                    }
                }
            }
        },
        500: get_server_error_response("POLL_OPTION_CREATION_FAILED", path)
    }

def get_poll_vote_responses(poll_id: int = 1, option_id: int = 1):
    """Generate complete response set for poll voting endpoint."""
    path = f"/api/v1/polls/{poll_id}/vote/{option_id}"
    
    return {
        200: {
            "description": "Vote recorded successfully",
            "model": "VoteResponse",
            "content": {
                CONTENT_TYPE_JSON: {
                    "example": {
                        "message": "Vote recorded successfully",
                        "vote": {
                            "id": 456,
                            "user_id": 123,
                            "poll_option_id": option_id,
                            "poll_id": poll_id,
                            "created_at": EXAMPLE_TIMESTAMP
                        },
                        "poll_id": poll_id,
                        "option_id": option_id,
                        "updated_vote_count": 15,
                        "timestamp": EXAMPLE_TIMESTAMP
                    }
                }
            }
        },
        400: {
            "description": "Business logic error - poll voting restrictions",
            "model": "BusinessErrorResponse",
            "content": {
                CONTENT_TYPE_JSON: {
                    "examples": {
                        "poll_inactive": {
                            "summary": "Poll is not active",
                            "value": {
                                "message": "Cannot vote on an inactive poll",
                                "error_code": "POLL_INACTIVE",
                                "poll_id": poll_id,
                                "timestamp": EXAMPLE_TIMESTAMP,
                                "path": path
                            }
                        },
                        "already_voted": {
                            "summary": "User already voted",
                            "value": {
                                "message": "User has already voted on this poll",
                                "error_code": "ALREADY_VOTED",
                                "poll_id": poll_id,
                                "existing_vote_option_id": 2,
                                "timestamp": EXAMPLE_TIMESTAMP,
                                "path": path
                            }
                        },
                        "vote_limit_exceeded": {
                            "summary": "Daily vote limit exceeded",
                            "value": {
                                "message": "Daily vote limit exceeded",
                                "error_code": "VOTE_LIMIT_EXCEEDED",
                                "current_votes": 1000,
                                "max_allowed": 1000,
                                "timestamp": EXAMPLE_TIMESTAMP,
                                "path": path
                            }
                        }
                    }
                }
            }
        },
        401: {
            "description": "Authentication required for private polls",
            "model": "AuthErrorResponse",
            "content": {
                CONTENT_TYPE_JSON: {
                    "examples": {
                        "auth_required_private": {
                            "summary": "Authentication required for private poll voting",
                            "value": {
                                "message": "Authentication required to vote on this private poll",
                                "error_code": "AUTHENTICATION_REQUIRED",
                                "poll_id": poll_id,
                                "hint": "This is a private poll that requires authentication",
                                "timestamp": EXAMPLE_TIMESTAMP,
                                "path": path
                            }
                        },
                        "invalid_token": {
                            "summary": "Invalid authentication token",
                            "value": {
                                "message": "Invalid authentication credentials",
                                "error_code": "INVALID_CREDENTIALS",
                                "timestamp": EXAMPLE_TIMESTAMP,
                                "path": path
                            }
                        }
                    }
                }
            }
        },
        403: {
            "description": "Access denied to private poll",
            "model": "AuthErrorResponse",
            "content": {
                CONTENT_TYPE_JSON: {
                    "example": {
                        "message": "Access denied to this private poll",
                        "error_code": "ACCESS_DENIED",
                        "poll_id": poll_id,
                        "owner_id": 456,
                        "hint": "This poll is private and you don't have access",
                        "timestamp": EXAMPLE_TIMESTAMP,
                        "path": path
                    }
                }
            }
        },
        404: {
            "description": "Poll or option not found",
            "model": "BusinessErrorResponse", 
            "content": {
                CONTENT_TYPE_JSON: {
                    "examples": {
                        "poll_not_found": {
                            "summary": "Poll not found",
                            "value": {
                                "message": "Poll not found",
                                "error_code": "POLL_NOT_FOUND",
                                "poll_id": poll_id,
                                "timestamp": EXAMPLE_TIMESTAMP,
                                "path": path
                            }
                        },
                        "option_not_found": {
                            "summary": "Poll option not found",
                            "value": {
                                "message": "Poll option not found",
                                "error_code": "POLL_OPTION_NOT_FOUND",
                                "poll_id": poll_id,
                                "option_id": option_id,
                                "timestamp": EXAMPLE_TIMESTAMP,
                                "path": path
                            }
                        },
                        "option_not_in_poll": {
                            "summary": "Option doesn't belong to poll",
                            "value": {
                                "message": "The specified option does not belong to this poll",
                                "error_code": "OPTION_NOT_IN_POLL",
                                "poll_id": poll_id,
                                "option_id": option_id,
                                "actual_poll_id": 999,
                                "timestamp": EXAMPLE_TIMESTAMP,
                                "path": path
                            }
                        }
                    }
                }
            }
        },
        422: {
            "description": "Validation error",
            "model": "ValidationErrorResponse",
            "content": {
                CONTENT_TYPE_JSON: {
                    "examples": {
                        "invalid_poll_id": {
                            "summary": "Invalid poll ID format",
                            "value": {
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
                                "poll_id": poll_id,
                                "timestamp": EXAMPLE_TIMESTAMP,
                                "path": path
                            }
                        },
                        "invalid_option_id": {
                            "summary": "Invalid option ID format",
                            "value": {
                                "message": "Validation failed",
                                "error_code": "VALIDATION_ERROR",
                                "errors": [
                                    {
                                        "loc": ["path", "option_id"],
                                        "msg": "Option ID must be greater than 0",
                                        "type": "value_error.number.not_gt",
                                        "ctx": {"limit_value": 0}
                                    }
                                ],
                                "option_id": option_id,
                                "timestamp": EXAMPLE_TIMESTAMP,
                                "path": path
                            }
                        }
                    }
                }
            }
        },
        500: get_server_error_response("POLL_VOTE_FAILED", path)
    }