"""
User-specific response definitions for FastAPI endpoints.

This module contains response configurations specific to user operations,
building upon common responses for maximum reusability and professional API documentation.
"""

from .common_responses import (
    AUTH_ERROR_RESPONSE,
    get_validation_error_response,
    get_server_error_response,
    CONTENT_TYPE_JSON,
    EXAMPLE_TIMESTAMP
)

# Constants for user paths
USERS_BASE_PATH = "/api/v1/users"
USER_PROFILE_PATH = f"{USERS_BASE_PATH}/me"
USER_CREATE_PATH = f"{USERS_BASE_PATH}/"
USER_UPDATE_PATH = f"{USERS_BASE_PATH}/me"

# Constants for repeated messages
USER_PROFILE_RETRIEVED = "User profile retrieved successfully"
USER_CREATED_SUCCESSFULLY = "User created successfully"
USER_UPDATED_SUCCESSFULLY = "User profile updated successfully"
VALIDATION_FAILED = "Validation failed"
FIELD_REQUIRED = "field required"
VALUE_ERROR_MISSING = "value_error.missing"
EMAIL_ALREADY_REGISTERED = "Email already registered"
USER_NOT_FOUND_MSG = "User not found"

# User success response examples
USER_PROFILE_EXAMPLE = {
    "id": 1,
    "username": "johndoe",
    "email": "john.doe@example.com",
    "full_name": "John Doe",
    "is_active": True
}

USER_CREATION_SUCCESS_EXAMPLE = {
    "id": 2,
    "username": "newuser",
    "email": "newuser@example.com",
    "full_name": "New User",
    "is_active": True
}

USER_UPDATE_SUCCESS_EXAMPLE = {
    "id": 1,
    "username": "johndoe",
    "email": "john.updated@example.com",
    "full_name": "John Updated",
    "is_active": True
}

# User error examples
USER_NOT_FOUND_EXAMPLE = {
    "message": USER_NOT_FOUND_MSG,
    "error_code": "USER_NOT_FOUND",
    "user_id": 999,
    "timestamp": EXAMPLE_TIMESTAMP,
    "path": USER_PROFILE_PATH
}

DUPLICATE_EMAIL_EXAMPLE = {
    "message": EMAIL_ALREADY_REGISTERED,
    "error_code": "DUPLICATE_EMAIL",
    "email": "existing@example.com",
    "timestamp": EXAMPLE_TIMESTAMP,
    "path": USER_CREATE_PATH
}

# Validation error examples specific to users
USER_VALIDATION_EXAMPLES = {
    "invalid_email": {
        "summary": "Invalid email format",
        "value": {
            "message": VALIDATION_FAILED,
            "error_code": "VALIDATION_ERROR",
            "errors": [
                {
                    "loc": ["body", "email"],
                    "msg": "value is not a valid email address",
                    "type": "value_error.email"
                }
            ],
            "timestamp": EXAMPLE_TIMESTAMP,
            "path": USER_CREATE_PATH
        }
    },
    "short_username": {
        "summary": "Username too short",
        "value": {
            "message": VALIDATION_FAILED,
            "error_code": "VALIDATION_ERROR",
            "errors": [
                {
                    "loc": ["body", "username"],
                    "msg": "ensure this value has at least 3 characters",
                    "type": "value_error.any_str.min_length",
                    "ctx": {"limit_value": 3}
                }
            ],
            "timestamp": EXAMPLE_TIMESTAMP,
            "path": USER_CREATE_PATH
        }
    },
    "long_username": {
        "summary": "Username too long",
        "value": {
            "message": VALIDATION_FAILED,
            "error_code": "VALIDATION_ERROR",
            "errors": [
                {
                    "loc": ["body", "username"],
                    "msg": "ensure this value has at most 50 characters",
                    "type": "value_error.any_str.max_length",
                    "ctx": {"limit_value": 50}
                }
            ],
            "timestamp": EXAMPLE_TIMESTAMP,
            "path": USER_CREATE_PATH
        }
    },
    "missing_required_fields": {
        "summary": "Missing required fields for user creation",
        "value": {
            "message": VALIDATION_FAILED,
            "error_code": "VALIDATION_ERROR",
            "errors": [
                {
                    "loc": ["body", "email"],
                    "msg": FIELD_REQUIRED,
                    "type": VALUE_ERROR_MISSING
                },
                {
                    "loc": ["body", "username"],
                    "msg": FIELD_REQUIRED,
                    "type": VALUE_ERROR_MISSING
                },
                {
                    "loc": ["body", "password"],
                    "msg": FIELD_REQUIRED,
                    "type": VALUE_ERROR_MISSING
                }
            ],
            "timestamp": EXAMPLE_TIMESTAMP,
            "path": USER_CREATE_PATH
        }
    }
}

def get_user_profile_responses():
    """Generate complete response set for user profile endpoint."""
    path = USER_PROFILE_PATH
    
    return {
        200: {
            "description": USER_PROFILE_RETRIEVED,
            "content": {
                CONTENT_TYPE_JSON: {
                    "example": USER_PROFILE_EXAMPLE
                }
            }
        },
        401: AUTH_ERROR_RESPONSE,
        500: get_server_error_response("USER_PROFILE_RETRIEVAL_FAILED", path)
    }

def get_user_creation_responses():
    """Generate complete response set for user creation endpoint."""
    path = USER_CREATE_PATH
    
    return {
        201: {
            "description": USER_CREATED_SUCCESSFULLY,
            "content": {
                CONTENT_TYPE_JSON: {
                    "example": USER_CREATION_SUCCESS_EXAMPLE
                }
            }
        },
        400: {
            "description": "Business logic error",
            "content": {
                CONTENT_TYPE_JSON: {
                    "examples": {
                        "duplicate_email": {
                            "summary": "Email already registered",
                            "value": DUPLICATE_EMAIL_EXAMPLE
                        }
                    }
                }
            }
        },
        422: {
            "description": "Validation error",
            "content": {
                CONTENT_TYPE_JSON: {
                    "examples": USER_VALIDATION_EXAMPLES
                }
            }
        },
        500: get_server_error_response("USER_CREATION_FAILED", path)
    }

def get_user_update_responses():
    """Generate complete response set for user profile update endpoint."""
    path = USER_UPDATE_PATH
    
    return {
        200: {
            "description": USER_UPDATED_SUCCESSFULLY,
            "content": {
                CONTENT_TYPE_JSON: {
                    "example": USER_UPDATE_SUCCESS_EXAMPLE
                }
            }
        },
        400: {
            "description": "Business logic error",
            "content": {
                CONTENT_TYPE_JSON: {
                    "examples": {
                        "duplicate_email": {
                            "summary": "Email already in use by another user",
                            "value": {
                                **DUPLICATE_EMAIL_EXAMPLE,
                                "path": path,
                                "hint": "This email is already registered to another user"
                            }
                        }
                    }
                }
            }
        },
        401: AUTH_ERROR_RESPONSE,
        404: {
            "description": USER_NOT_FOUND_MSG,
            "content": {
                CONTENT_TYPE_JSON: {
                    "example": USER_NOT_FOUND_EXAMPLE
                }
            }
        },
        422: {
            "description": "Validation error",
            "content": {
                CONTENT_TYPE_JSON: {
                    "examples": {
                        **USER_VALIDATION_EXAMPLES,
                        "invalid_update_data": {
                            "summary": "Invalid update data",
                            "value": {
                                "message": VALIDATION_FAILED,
                                "error_code": "VALIDATION_ERROR",
                                "errors": [
                                    {
                                        "loc": ["body", "email"],
                                        "msg": "value is not a valid email address",
                                        "type": "value_error.email"
                                    }
                                ],
                                "timestamp": EXAMPLE_TIMESTAMP,
                                "path": path
                            }
                        }
                    }
                }
            }
        },
        500: get_server_error_response("USER_UPDATE_FAILED", path)
    }

# Convenience functions for common user error responses
def get_user_not_found_response(path: str, user_id: int = None):
    """Generate user not found error response with context."""
    return {
        "description": USER_NOT_FOUND_MSG,
        "content": {
            CONTENT_TYPE_JSON: {
                "example": {
                    "message": USER_NOT_FOUND_MSG,
                    "error_code": "USER_NOT_FOUND",
                    "user_id": user_id,
                    "timestamp": EXAMPLE_TIMESTAMP,
                    "path": path
                }
            }
        }
    }

def get_user_business_error_response(path: str):
    """Generate business logic error response for user operations."""
    return {
        "description": "Business logic validation failed",
        "content": {
            CONTENT_TYPE_JSON: {
                "examples": {
                    "duplicate_email": {
                        "summary": "Email already registered",
                        "value": {
                            "message": EMAIL_ALREADY_REGISTERED,
                            "error_code": "DUPLICATE_EMAIL",
                            "email": "existing@example.com",
                            "timestamp": EXAMPLE_TIMESTAMP,
                            "path": path,
                            "hint": "Please use a different email address"
                        }
                    },
                    "user_limit_exceeded": {
                        "summary": "User creation rate limit exceeded",
                        "value": {
                            "message": "Too many user creation attempts",
                            "error_code": "RATE_LIMIT_EXCEEDED",
                            "retry_after": "300",
                            "timestamp": EXAMPLE_TIMESTAMP,
                            "path": path
                        }
                    }
                }
            }
        }
    }