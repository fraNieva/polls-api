from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from datetime import datetime, timezone
import logging
import asyncio
from typing import Dict, Any
import traceback
import uuid

logger = logging.getLogger(__name__)

async def validation_exception_handler(request: Request, exc: ValidationError):
    """
    Custom handler for Pydantic validation errors
    
    Why async? 
    1. FastAPI requires async for exception handlers
    2. Allows future async operations (logging, monitoring)
    3. Non-blocking error processing
    """
    # Generate unique request ID for tracing
    request_id = str(uuid.uuid4())[:8]
    
    # Enhanced logging with request context
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")
    
    logger.warning(
        f"Validation error [ID: {request_id}] - "
        f"Path: {request.url.path} - "
        f"IP: {client_ip} - "
        f"Errors: {len(exc.errors())} - "
        f"Details: {exc.errors()}"
    )
    
    # Future: Could add async operations here
    # await send_to_monitoring_service(request_id, exc)
    # await log_to_external_service(request_id, exc)
    
    return JSONResponse(
        status_code=422,
        content={
            "message": "Validation failed",
            "error_code": "VALIDATION_ERROR",
            "errors": exc.errors(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "path": str(request.url.path),
            "request_id": request_id
        }
    )

async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Enhanced HTTP exception handler
    
    Why async?
    1. Required by FastAPI's ASGI architecture
    2. Enables non-blocking error processing
    3. Future-proof for async logging/monitoring
    """
    request_id = str(uuid.uuid4())[:8]
    client_ip = request.client.host if request.client else "unknown"
    
    # Enhanced logging based on error severity
    if exc.status_code >= 500:
        logger.error(
            f"Server error [ID: {request_id}] - "
            f"Status: {exc.status_code} - "
            f"Path: {request.url.path} - "
            f"IP: {client_ip} - "
            f"Detail: {exc.detail}"
        )
    elif exc.status_code >= 400:
        logger.warning(
            f"Client error [ID: {request_id}] - "
            f"Status: {exc.status_code} - "
            f"Path: {request.url.path} - "
            f"IP: {client_ip}"
        )
    
    # Format response based on detail type
    if isinstance(exc.detail, dict):
        response_content = {
            **exc.detail,  # Include all existing detail fields
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "path": str(request.url.path),
            "request_id": request_id
        }
    else:
        response_content = {
            "message": str(exc.detail),
            "error_code": "HTTP_ERROR",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "path": str(request.url.path),
            "request_id": request_id
        }
    
    return JSONResponse(
        status_code=exc.status_code,
        content=response_content
    )


async def database_exception_handler(request: Request, exc: Exception):
    """
    Handler for database-related exceptions
    
    Demonstrates REAL async usage - logging to external services
    """
    request_id = str(uuid.uuid4())[:8]
    
    logger.error(
        f"Database error [ID: {request_id}] - "
        f"Path: {request.url.path} - "
        f"Error: {str(exc)} - "
        f"Type: {type(exc).__name__}"
    )
    
    # Example of REAL async operation - could be:
    # - Sending error to external monitoring service
    # - Logging to remote logging service
    # - Notifying administrators via async notification service
    
    # Simulate async monitoring (replace with real service)
    try:
        # This is where you'd have real async operations:
        # await monitoring_service.report_database_error(request_id, exc)
        # await notification_service.alert_admins(exc)
        await asyncio.sleep(0.01)  # Simulate async I/O without blocking
    except Exception as monitoring_error:
        logger.error(f"Failed to report error to monitoring: {monitoring_error}")
    
    return JSONResponse(
        status_code=500,
        content={
            "message": "Database operation failed",
            "error_code": "DATABASE_ERROR",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "path": str(request.url.path),
            "request_id": request_id,
            "hint": "Please try again later or contact support"
        }
    )


async def general_exception_handler(request: Request, exc: Exception):
    """
    Catch-all exception handler for unexpected errors
    
    Shows why async is crucial - handles errors without blocking other requests
    """
    request_id = str(uuid.uuid4())[:8]
    
    # Get full traceback for debugging
    tb_str = traceback.format_exc()
    
    logger.critical(
        f"Unexpected error [ID: {request_id}] - "
        f"Path: {request.url.path} - "
        f"Error: {str(exc)} - "
        f"Type: {type(exc).__name__} - "
        f"Traceback: {tb_str}"
    )
    
    # Async operations for critical errors
    try:
        # Real-world examples of what you might do asynchronously:
        # await emergency_notification_service.alert_developers(request_id, exc, tb_str)
        # await error_tracking_service.capture_exception(exc, request_context)
        # await metrics_service.increment_critical_error_counter()
        
        # Simulate async notification without blocking the response
        await asyncio.sleep(0.01)
    except Exception as notification_error:
        logger.error(f"Failed to send critical error notification: {notification_error}")
    
    return JSONResponse(
        status_code=500,
        content={
            "message": "An unexpected error occurred",
            "error_code": "INTERNAL_ERROR",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "path": str(request.url.path),
            "request_id": request_id
        }
    )