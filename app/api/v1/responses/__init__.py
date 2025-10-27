"""
Response definitions for FastAPI endpoints.

This module provides centralized response configurations for OpenAPI documentation,
promoting reusability and maintainability across all API endpoints.
"""

from .common_responses import (
    AUTH_ERROR_RESPONSE,
    VALIDATION_ERROR_RESPONSE, 
    SERVER_ERROR_RESPONSE,
    RATE_LIMIT_ERROR_RESPONSE,
    get_validation_error_response,
    get_server_error_response,
    common_validation_examples,
    common_server_error_example,
)

from .poll_responses import (
    get_poll_create_responses,
    get_poll_update_responses,
    get_poll_list_responses,
    get_user_polls_responses,
    get_single_poll_responses,
    POLL_SUCCESS_RESPONSES,
    POLL_ERROR_RESPONSES,
)

__all__ = [
    # Common responses
    "AUTH_ERROR_RESPONSE",
    "VALIDATION_ERROR_RESPONSE", 
    "SERVER_ERROR_RESPONSE",
    "RATE_LIMIT_ERROR_RESPONSE",
    "get_validation_error_response",
    "get_server_error_response",
    "common_validation_examples",
    "common_server_error_example",
    
    # Poll-specific responses
    "get_poll_create_responses",
    "get_poll_update_responses", 
    "get_poll_list_responses",
    "get_user_polls_responses",
    "get_single_poll_responses",
    "POLL_SUCCESS_RESPONSES",
    "POLL_ERROR_RESPONSES",
]