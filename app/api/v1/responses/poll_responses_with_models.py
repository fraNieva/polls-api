"""
Poll-specific response definitions using string-based model references.
This approach avoids Pydantic v2 forward reference issues while maintaining detailed documentation.
"""

# Constants for poll paths and content types
POLLS_BASE_PATH = "/api/v1/polls/"
MY_POLLS_PATH = "/api/v1/polls/my-polls"
CONTENT_TYPE_JSON = "application/json"
EXAMPLE_TIMESTAMP = "2024-01-01T12:00:00Z"

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

# Error response examples
BUSINESS_ERROR_EXAMPLE = {
    "message": "A poll with this title already exists",
    "error_code": "DUPLICATE_POLL_TITLE",
    "details": {"existing_poll_id": 123},
    "timestamp": EXAMPLE_TIMESTAMP,
    "path": POLLS_BASE_PATH
}

VALIDATION_ERROR_EXAMPLE = {
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
    "path": POLLS_BASE_PATH
}

AUTH_ERROR_EXAMPLE = {
    "message": "Authentication required",
    "error_code": "AUTHENTICATION_REQUIRED",
    "timestamp": EXAMPLE_TIMESTAMP,
    "path": POLLS_BASE_PATH
}

NOT_FOUND_EXAMPLE = {
    "message": "Poll not found",
    "error_code": "POLL_NOT_FOUND",
    "poll_id": 999,
    "timestamp": EXAMPLE_TIMESTAMP,
    "path": POLLS_BASE_PATH
}

FORBIDDEN_EXAMPLE = {
    "message": "Not authorized to update this poll",
    "error_code": "NOT_AUTHORIZED_UPDATE",
    "poll_id": 1,
    "owner_id": 2,
    "timestamp": EXAMPLE_TIMESTAMP,
    "path": POLLS_BASE_PATH
}

# Response function implementations using string references
def get_poll_create_responses(**kwargs):
    """Generate complete response set for poll creation endpoint."""
    return {
        201: {
            "description": "Poll created successfully",
            "content": {
                CONTENT_TYPE_JSON: {
                    "example": POLL_SUCCESS_EXAMPLE,
                    # Reference model as string to avoid forward reference issues
                    "schema": {"$ref": "#/components/schemas/PollRead"}
                }
            }
        },
        400: {
            "description": "Business logic error",
            "content": {
                CONTENT_TYPE_JSON: {
                    "examples": {
                        "duplicate_poll": {
                            "summary": "Duplicate poll title",
                            "value": BUSINESS_ERROR_EXAMPLE
                        }
                    },
                    "schema": {"$ref": "#/components/schemas/BusinessErrorResponse"}
                }
            }
        },
        401: {
            "description": "Authentication failed",
            "content": {
                CONTENT_TYPE_JSON: {
                    "example": AUTH_ERROR_EXAMPLE,
                    "schema": {"$ref": "#/components/schemas/AuthErrorResponse"}
                }
            }
        },
        422: {
            "description": "Validation failed",
            "content": {
                CONTENT_TYPE_JSON: {
                    "examples": {
                        "invalid_title": {
                            "summary": "Invalid poll title",
                            "value": VALIDATION_ERROR_EXAMPLE
                        }
                    },
                    "schema": {"$ref": "#/components/schemas/ValidationErrorResponse"}
                }
            }
        }
    }

def get_poll_list_responses(**kwargs):
    """Generate complete response set for poll listing endpoint."""
    return {
        200: {
            "description": "Polls retrieved successfully",
            "content": {
                CONTENT_TYPE_JSON: {
                    "example": PAGINATED_POLLS_EXAMPLE,
                    "schema": {"$ref": "#/components/schemas/PaginatedResponse[PollRead]"}
                }
            }
        },
        422: {
            "description": "Validation failed",
            "content": {
                CONTENT_TYPE_JSON: {
                    "examples": {
                        "invalid_page": {
                            "summary": "Invalid page parameter",
                            "value": {
                                "message": "Validation failed",
                                "error_code": "VALIDATION_ERROR",
                                "errors": [
                                    {
                                        "loc": ["query", "page"],
                                        "msg": "ensure this value is greater than 0",
                                        "type": "value_error.number.not_gt",
                                        "ctx": {"limit_value": 0}
                                    }
                                ],
                                "timestamp": EXAMPLE_TIMESTAMP,
                                "path": POLLS_BASE_PATH
                            }
                        }
                    },
                    "schema": {"$ref": "#/components/schemas/ValidationErrorResponse"}
                }
            }
        }
    }

def get_poll_get_responses(poll_id: int = 1, **kwargs):
    """Generate complete response set for single poll retrieval."""
    path = f"/api/v1/polls/{poll_id}"
    return {
        200: {
            "description": "Poll retrieved successfully",
            "content": {
                CONTENT_TYPE_JSON: {
                    "example": POLL_WITH_OPTIONS_EXAMPLE,
                    "schema": {"$ref": "#/components/schemas/PollRead"}
                }
            }
        },
        404: {
            "description": "Poll not found",
            "content": {
                CONTENT_TYPE_JSON: {
                    "example": {**NOT_FOUND_EXAMPLE, "path": path},
                    "schema": {"$ref": "#/components/schemas/BusinessErrorResponse"}
                }
            }
        },
        422: {
            "description": "Validation failed",
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
                    },
                    "schema": {"$ref": "#/components/schemas/ValidationErrorResponse"}
                }
            }
        }
    }

def get_poll_update_responses(poll_id: int = 1, **kwargs):
    """Generate complete response set for poll update endpoint."""
    path = f"/api/v1/polls/{poll_id}"
    return {
        200: {
            "description": "Poll updated successfully",
            "content": {
                CONTENT_TYPE_JSON: {
                    "example": POLL_SUCCESS_EXAMPLE,
                    "schema": {"$ref": "#/components/schemas/PollRead"}
                }
            }
        },
        400: {
            "description": "Business logic error",
            "content": {
                CONTENT_TYPE_JSON: {
                    "examples": {
                        "duplicate_title": {
                            "summary": "Duplicate poll title",
                            "value": {**BUSINESS_ERROR_EXAMPLE, "path": path}
                        }
                    },
                    "schema": {"$ref": "#/components/schemas/BusinessErrorResponse"}
                }
            }
        },
        401: {
            "description": "Authentication failed",
            "content": {
                CONTENT_TYPE_JSON: {
                    "example": {**AUTH_ERROR_EXAMPLE, "path": path},
                    "schema": {"$ref": "#/components/schemas/AuthErrorResponse"}
                }
            }
        },
        403: {
            "description": "Access forbidden - not poll owner",
            "content": {
                CONTENT_TYPE_JSON: {
                    "example": {**FORBIDDEN_EXAMPLE, "path": path},
                    "schema": {"$ref": "#/components/schemas/BusinessErrorResponse"}
                }
            }
        },
        404: {
            "description": "Poll not found",
            "content": {
                CONTENT_TYPE_JSON: {
                    "example": {**NOT_FOUND_EXAMPLE, "path": path},
                    "schema": {"$ref": "#/components/schemas/BusinessErrorResponse"}
                }
            }
        },
        422: {
            "description": "Validation failed",
            "content": {
                CONTENT_TYPE_JSON: {
                    "example": {**VALIDATION_ERROR_EXAMPLE, "path": path},
                    "schema": {"$ref": "#/components/schemas/ValidationErrorResponse"}
                }
            }
        }
    }

def get_poll_delete_responses(poll_id: int = 1, **kwargs):
    """Generate complete response set for poll deletion endpoint."""
    path = f"/api/v1/polls/{poll_id}"
    return {
        204: {
            "description": "Poll deleted successfully"
        },
        401: {
            "description": "Authentication failed",
            "content": {
                CONTENT_TYPE_JSON: {
                    "example": {**AUTH_ERROR_EXAMPLE, "path": path},
                    "schema": {"$ref": "#/components/schemas/AuthErrorResponse"}
                }
            }
        },
        403: {
            "description": "Access forbidden - not poll owner",
            "content": {
                CONTENT_TYPE_JSON: {
                    "example": {**FORBIDDEN_EXAMPLE, "path": path},
                    "schema": {"$ref": "#/components/schemas/BusinessErrorResponse"}
                }
            }
        },
        404: {
            "description": "Poll not found",
            "content": {
                CONTENT_TYPE_JSON: {
                    "example": {**NOT_FOUND_EXAMPLE, "path": path},
                    "schema": {"$ref": "#/components/schemas/BusinessErrorResponse"}
                }
            }
        }
    }

def get_poll_vote_responses(poll_id: int = 1, **kwargs):
    """Generate complete response set for poll voting endpoint."""
    path = f"/api/v1/polls/{poll_id}/vote"
    return {
        200: {
            "description": "Vote recorded successfully",
            "content": {
                CONTENT_TYPE_JSON: {
                    "example": {
                        "message": "Vote recorded successfully",
                        "poll_id": poll_id,
                        "option_id": 1,
                        "vote_count": 6
                    },
                    "schema": {"$ref": "#/components/schemas/VoteResponse"}
                }
            }
        },
        400: {
            "description": "Business logic error",
            "content": {
                CONTENT_TYPE_JSON: {
                    "examples": {
                        "poll_inactive": {
                            "summary": "Poll is not active",
                            "value": {
                                "message": "Cannot vote on inactive poll",
                                "error_code": "POLL_NOT_ACTIVE",
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
                                "timestamp": EXAMPLE_TIMESTAMP,
                                "path": path
                            }
                        }
                    },
                    "schema": {"$ref": "#/components/schemas/BusinessErrorResponse"}
                }
            }
        },
        401: {
            "description": "Authentication failed",
            "content": {
                CONTENT_TYPE_JSON: {
                    "example": {**AUTH_ERROR_EXAMPLE, "path": path},
                    "schema": {"$ref": "#/components/schemas/AuthErrorResponse"}
                }
            }
        },
        404: {
            "description": "Poll or option not found",
            "content": {
                CONTENT_TYPE_JSON: {
                    "examples": {
                        "poll_not_found": {
                            "summary": "Poll not found",
                            "value": {**NOT_FOUND_EXAMPLE, "path": path}
                        },
                        "option_not_found": {
                            "summary": "Poll option not found",
                            "value": {
                                "message": "Poll option not found",
                                "error_code": "POLL_OPTION_NOT_FOUND",
                                "poll_id": poll_id,
                                "option_id": 999,
                                "timestamp": EXAMPLE_TIMESTAMP,
                                "path": path
                            }
                        }
                    },
                    "schema": {"$ref": "#/components/schemas/BusinessErrorResponse"}
                }
            }
        }
    }

def get_user_polls_responses(**kwargs):
    """Generate complete response set for user polls endpoint."""
    return {
        200: {
            "description": "User polls retrieved successfully",
            "content": {
                CONTENT_TYPE_JSON: {
                    "example": {
                        "items": [POLL_WITH_OPTIONS_EXAMPLE],
                        "total": 1,
                        "page": 1,
                        "size": 10,
                        "pages": 1
                    },
                    "schema": {"$ref": "#/components/schemas/PaginatedResponse[PollRead]"}
                }
            }
        },
        401: {
            "description": "Authentication failed",
            "content": {
                CONTENT_TYPE_JSON: {
                    "example": {**AUTH_ERROR_EXAMPLE, "path": MY_POLLS_PATH},
                    "schema": {"$ref": "#/components/schemas/AuthErrorResponse"}
                }
            }
        }
    }

# Alias for single poll responses
def get_single_poll_responses(**kwargs):
    """Alias for get_poll_get_responses."""
    return get_poll_get_responses(**kwargs)

def get_poll_option_create_responses(**kwargs):
    """Generate complete response set for poll option creation."""
    return {
        201: {
            "description": "Poll option created successfully",
            "content": {
                CONTENT_TYPE_JSON: {
                    "example": {
                        "id": 3,
                        "text": "Go",
                        "vote_count": 0
                    },
                    "schema": {"$ref": "#/components/schemas/PollOptionRead"}
                }
            }
        },
        400: {
            "description": "Business logic error",
            "content": {
                CONTENT_TYPE_JSON: {
                    "example": BUSINESS_ERROR_EXAMPLE,
                    "schema": {"$ref": "#/components/schemas/BusinessErrorResponse"}
                }
            }
        },
        401: {
            "description": "Authentication failed",
            "content": {
                CONTENT_TYPE_JSON: {
                    "example": AUTH_ERROR_EXAMPLE,
                    "schema": {"$ref": "#/components/schemas/AuthErrorResponse"}
                }
            }
        }
    }