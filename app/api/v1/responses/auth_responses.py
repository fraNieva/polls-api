"""
Authentication-specific response definitions for FastAPI endpoints.

This module contains response configurations specific to authentication operations,
building upon common responses for maximum reusability and professional API documentation.
"""

from .common_responses import (
    AUTH_ERROR_RESPONSE,
    get_validation_error_response,
    get_server_error_response,
    RATE_LIMIT_ERROR_RESPONSE,
    CONTENT_TYPE_JSON,
    EXAMPLE_TIMESTAMP
)

# Constants for auth paths
AUTH_BASE_PATH = "/api/v1/auth"
REGISTER_PATH = f"{AUTH_BASE_PATH}/register"
LOGIN_PATH = f"{AUTH_BASE_PATH}/login"
TOKEN_PATH = f"{AUTH_BASE_PATH}/token"

# Constants for repeated messages
EMAIL_ALREADY_REGISTERED = "Email already registered"
USERNAME_ALREADY_REGISTERED = "Username already registered"
VALIDATION_FAILED = "Validation failed"
FIELD_REQUIRED = "field required"
VALUE_ERROR_MISSING = "value_error.missing"
RATE_LIMIT_EXCEEDED_DESC = "Rate limit exceeded"

# Auth success response examples
USER_REGISTRATION_SUCCESS_EXAMPLE = {
    "id": 1,
    "username": "newuser",
    "email": "newuser@example.com",
    "full_name": "New User",
    "is_active": True
}

TOKEN_SUCCESS_EXAMPLE = {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
}

# Auth error examples
DUPLICATE_USER_EXAMPLE = {
    "message": EMAIL_ALREADY_REGISTERED,
    "error_code": "DUPLICATE_EMAIL",
    "email": "existing@example.com",
    "timestamp": EXAMPLE_TIMESTAMP,
    "path": REGISTER_PATH
}

DUPLICATE_USERNAME_EXAMPLE = {
    "message": USERNAME_ALREADY_REGISTERED,
    "error_code": "DUPLICATE_USERNAME", 
    "username": "existinguser",
    "timestamp": EXAMPLE_TIMESTAMP,
    "path": REGISTER_PATH
}

INVALID_CREDENTIALS_EXAMPLE = {
    "message": "Email o contraseña incorrectos",
    "error_code": "INVALID_CREDENTIALS",
    "timestamp": EXAMPLE_TIMESTAMP,
    "path": LOGIN_PATH
}

RATE_LIMIT_AUTH_EXAMPLE = {
    "message": "Too many authentication attempts. Please try again later.",
    "error_code": "RATE_LIMIT_EXCEEDED",
    "retry_after": "300",
    "timestamp": EXAMPLE_TIMESTAMP,
    "path": LOGIN_PATH
}

# Validation error examples specific to auth
AUTH_VALIDATION_EXAMPLES = {
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
            "path": REGISTER_PATH
        }
    },
    "short_password": {
        "summary": "Password too short",
        "value": {
            "message": VALIDATION_FAILED,
            "error_code": "VALIDATION_ERROR",
            "errors": [
                {
                    "loc": ["body", "password"],
                    "msg": "ensure this value has at least 8 characters",
                    "type": "value_error.any_str.min_length",
                    "ctx": {"limit_value": 8}
                }
            ],
            "timestamp": EXAMPLE_TIMESTAMP,
            "path": REGISTER_PATH
        }
    },
    "missing_fields": {
        "summary": "Missing required fields",
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
                    "loc": ["body", "password"],
                    "msg": FIELD_REQUIRED,
                    "type": VALUE_ERROR_MISSING
                }
            ],
            "timestamp": EXAMPLE_TIMESTAMP,
            "path": REGISTER_PATH
        }
    }
}

def get_registration_responses():
    """Generate complete response set for user registration endpoint."""
    path = REGISTER_PATH
    
    return {
        201: {
            "description": "User registered successfully",
            "content": {
                CONTENT_TYPE_JSON: {
                    "example": USER_REGISTRATION_SUCCESS_EXAMPLE
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
                            "value": DUPLICATE_USER_EXAMPLE
                        },
                        "duplicate_username": {
                            "summary": "Username already registered", 
                            "value": DUPLICATE_USERNAME_EXAMPLE
                        }
                    }
                }
            }
        },
        422: {
            "description": "Validation error",
            "content": {
                CONTENT_TYPE_JSON: {
                    "examples": AUTH_VALIDATION_EXAMPLES
                }
            }
        },
        429: {
            "description": "Rate limit exceeded",
            "content": {
                CONTENT_TYPE_JSON: {
                    "example": RATE_LIMIT_AUTH_EXAMPLE
                }
            }
        },
        500: get_server_error_response("USER_REGISTRATION_FAILED", path)
    }

def get_login_responses():
    """Generate complete response set for user login endpoint."""
    path = LOGIN_PATH
    
    return {
        200: {
            "description": "Login successful",
            "content": {
                CONTENT_TYPE_JSON: {
                    "example": TOKEN_SUCCESS_EXAMPLE
                }
            }
        },
        401: {
            "description": "Invalid credentials",
            "content": {
                CONTENT_TYPE_JSON: {
                    "example": INVALID_CREDENTIALS_EXAMPLE
                }
            }
        },
        422: {
            "description": "Validation error",
            "content": {
                CONTENT_TYPE_JSON: {
                    "examples": {
                        "missing_email": {
                            "summary": "Missing email field",
                            "value": {
                                "message": VALIDATION_FAILED,
                                "error_code": "VALIDATION_ERROR",
                                "errors": [
                                    {
                                        "loc": ["body", "email"],
                                        "msg": FIELD_REQUIRED,
                                        "type": VALUE_ERROR_MISSING
                                    }
                                ],
                                "timestamp": EXAMPLE_TIMESTAMP,
                                "path": path
                            }
                        },
                        "missing_password": {
                            "summary": "Missing password field", 
                            "value": {
                                "message": VALIDATION_FAILED,
                                "error_code": "VALIDATION_ERROR",
                                "errors": [
                                    {
                                        "loc": ["body", "password"],
                                        "msg": FIELD_REQUIRED,
                                        "type": VALUE_ERROR_MISSING
                                    }
                                ],
                                "timestamp": EXAMPLE_TIMESTAMP,
                                "path": path
                            }
                        },
                        "invalid_email": AUTH_VALIDATION_EXAMPLES["invalid_email"]
                    }
                }
            }
        },
        429: {
            "description": "Rate limit exceeded",
            "content": {
                CONTENT_TYPE_JSON: {
                    "example": RATE_LIMIT_AUTH_EXAMPLE
                }
            }
        },
        500: get_server_error_response("LOGIN_FAILED", path)
    }

def get_token_responses():
    """Generate complete response set for OAuth2 token endpoint."""
    path = TOKEN_PATH
    
    return {
        200: {
            "description": "Token generated successfully",
            "content": {
                CONTENT_TYPE_JSON: {
                    "example": TOKEN_SUCCESS_EXAMPLE
                }
            }
        },
        401: {
            "description": "Invalid credentials",
            "content": {
                CONTENT_TYPE_JSON: {
                    "example": {
                        **INVALID_CREDENTIALS_EXAMPLE,
                        "path": path,
                        "hint": "Enter your EMAIL ADDRESS in the 'username' field, not your username"
                    }
                }
            }
        },
        422: {
            "description": "Validation error - OAuth2 form data",
            "content": {
                CONTENT_TYPE_JSON: {
                    "examples": {
                        "missing_username": {
                            "summary": "Missing username (email) field",
                            "value": {
                                "message": VALIDATION_FAILED,
                                "error_code": "VALIDATION_ERROR",
                                "errors": [
                                    {
                                        "loc": ["body", "username"],
                                        "msg": FIELD_REQUIRED,
                                        "type": VALUE_ERROR_MISSING
                                    }
                                ],
                                "timestamp": EXAMPLE_TIMESTAMP,
                                "path": path,
                                "hint": "OAuth2 compatible endpoint - use 'username' field for email"
                            }
                        },
                        "missing_password": {
                            "summary": "Missing password field",
                            "value": {
                                "message": VALIDATION_FAILED, 
                                "error_code": "VALIDATION_ERROR",
                                "errors": [
                                    {
                                        "loc": ["body", "password"],
                                        "msg": FIELD_REQUIRED,
                                        "type": VALUE_ERROR_MISSING
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
        429: {
            "description": "Rate limit exceeded",
            "content": {
                CONTENT_TYPE_JSON: {
                    "example": {
                        **RATE_LIMIT_AUTH_EXAMPLE,
                        "path": path
                    }
                }
            }
        },
        500: get_server_error_response("TOKEN_GENERATION_FAILED", path)
    }

# Convenience functions for common auth error responses
def get_duplicate_email_response(path: str, email: str):
    """Generate duplicate email error response with context."""
    return {
        "description": EMAIL_ALREADY_REGISTERED,
        "content": {
            CONTENT_TYPE_JSON: {
                "example": {
                    "message": EMAIL_ALREADY_REGISTERED,
                    "error_code": "DUPLICATE_EMAIL",
                    "email": email,
                    "timestamp": EXAMPLE_TIMESTAMP,
                    "path": path,
                    "hint": "Try logging in instead, or use a different email address"
                }
            }
        }
    }

def get_duplicate_username_response(path: str, username: str):
    """Generate duplicate username error response with context."""
    return {
        "description": USERNAME_ALREADY_REGISTERED,
        "content": {
            CONTENT_TYPE_JSON: {
                "example": {
                    "message": USERNAME_ALREADY_REGISTERED,
                    "error_code": "DUPLICATE_USERNAME",
                    "username": username,
                    "timestamp": EXAMPLE_TIMESTAMP,
                    "path": path,
                    "hint": "Please choose a different username"
                }
            }
        }
    }

def get_auth_business_error_response(path: str):
    """Generate business logic error response for auth operations."""
    return {
        "description": "Business logic validation failed",
        "content": {
            CONTENT_TYPE_JSON: {
                "examples": {
                    "rate_limit": {
                        "summary": "Rate limit exceeded",
                        "value": {
                            "message": "Too many registration attempts",
                            "error_code": "RATE_LIMIT_EXCEEDED",
                            "retry_after": "300",
                            "timestamp": EXAMPLE_TIMESTAMP,
                            "path": path
                        }
                    },
                    "weak_password": {
                        "summary": "Password does not meet security requirements",
                        "value": {
                            "message": "Password does not meet security requirements",
                            "error_code": "WEAK_PASSWORD",
                            "requirements": [
                                "At least 8 characters",
                                "At least one special character",
                                "At least one number"
                            ],
                            "timestamp": EXAMPLE_TIMESTAMP,
                            "path": path
                        }
                    }
                }
            }
        }
    }