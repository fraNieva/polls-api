from pydantic import BaseModel
from typing import Optional, Any, Dict, List
from datetime import datetime

class ErrorDetail(BaseModel):
    """Individual error detail for validation errors"""
    loc: List[str]  # Location of the error (field path)
    msg: str        # Error message
    type: str       # Error type
    ctx: Optional[Dict[str, Any]] = None  # Additional context

class ValidationErrorResponse(BaseModel):
    """Response schema for validation errors (422)"""
    message: str = "Validation failed"
    error_code: str = "VALIDATION_ERROR"
    errors: List[ErrorDetail]
    timestamp: str
    path: str

class BusinessErrorResponse(BaseModel):
    """Response schema for business logic errors (400, 409, etc.)"""
    message: str
    error_code: str
    details: Optional[Dict[str, Any]] = None
    hint: Optional[str] = None
    timestamp: str
    path: str

class AuthErrorResponse(BaseModel):
    """Response schema for authentication/authorization errors (401, 403)"""
    message: str = "Authentication required"
    error_code: str = "AUTH_ERROR"
    timestamp: str
    path: str

class NotFoundErrorResponse(BaseModel):
    """Response schema for resource not found errors (404)"""
    message: str = "Resource not found"
    error_code: str = "NOT_FOUND"
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    timestamp: str
    path: str

class RateLimitErrorResponse(BaseModel):
    """Response schema for rate limit errors (429)"""
    message: str = "Rate limit exceeded"
    error_code: str = "RATE_LIMIT_EXCEEDED"
    retry_after: str  # Seconds until retry allowed
    limit: Optional[int] = None
    window: Optional[str] = None
    timestamp: str
    path: str

class ServerErrorResponse(BaseModel):
    """Response schema for internal server errors (500)"""
    message: str = "Internal server error"
    error_code: str = "INTERNAL_ERROR"
    request_id: Optional[str] = None  # For tracking
    timestamp: str
    path: str

# Generic error response that can handle any error type
class GenericErrorResponse(BaseModel):
    """Generic error response that can be used for any error"""
    message: str
    error_code: str
    status_code: int
    details: Optional[Dict[str, Any]] = None
    errors: Optional[List[ErrorDetail]] = None
    timestamp: str
    path: str
    request_id: Optional[str] = None