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

from .poll_responses_with_models import (
    get_poll_create_responses,
    get_poll_update_responses,
    get_poll_list_responses,
    get_user_polls_responses,
    get_single_poll_responses,
    get_poll_delete_responses,
    get_poll_option_create_responses,
    get_poll_vote_responses,
)

from .auth_responses import (
    get_registration_responses,
    get_login_responses,
    get_token_responses,
    get_duplicate_email_response,
    get_duplicate_username_response,
    get_auth_business_error_response,
)

from .user_responses import (
    get_user_profile_responses,
    get_user_creation_responses,
    get_user_update_responses,
    get_user_not_found_response,
    get_user_business_error_response,
)

# Add missing function alias
get_poll_get_responses = get_single_poll_responses

# Define missing constants as empty
POLL_SUCCESS_RESPONSES = {}
POLL_ERROR_RESPONSES = {}

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
    "get_poll_delete_responses",
    "get_poll_option_create_responses",
    "get_poll_vote_responses",
    "POLL_SUCCESS_RESPONSES",
    "POLL_ERROR_RESPONSES",
    
    # Auth-specific responses
    "get_registration_responses",
    "get_login_responses",
    "get_token_responses",
    "get_duplicate_email_response",
    "get_duplicate_username_response",
    "get_auth_business_error_response",
    
    # User-specific responses
    "get_user_profile_responses",
    "get_user_creation_responses",
    "get_user_update_responses",
    "get_user_not_found_response",
    "get_user_business_error_response",
]