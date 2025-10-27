"""
Application Constants

Centralized location for all application constants, organized by domain.
This makes it easy to maintain and update values across the entire application.
"""

# =============================================================================
# API Configuration
# =============================================================================

class APIConfig:
    """API-level configuration constants"""
    
    # API Versioning
    API_V1_PREFIX = "/api/v1"
    API_VERSION = "1.0.0"
    API_TITLE = "Polls API"
    API_DESCRIPTION = """
    A comprehensive polling API that allows users to create polls, vote on them, and view results.
    
    ## Features
    - User authentication and registration
    - Poll creation and management
    - Voting system with constraints
    - Real-time poll results
    """
    
    # CORS Configuration
    ALLOWED_ORIGINS = [
        "http://localhost:3000",  # React dev server
        "http://localhost:8080",  # Vue dev server
        "http://localhost:4200",  # Angular dev server
    ]
    
    # Request limits
    MAX_REQUEST_SIZE = 10 * 1024 * 1024  # 10MB
    REQUEST_TIMEOUT = 30  # seconds


# =============================================================================
# Authentication & Security
# =============================================================================

class AuthConfig:
    """Authentication and security constants"""
    
    # JWT Configuration
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    REFRESH_TOKEN_EXPIRE_DAYS = 7
    ALGORITHM = "HS256"
    TOKEN_TYPE = "bearer"
    
    # Password requirements
    MIN_PASSWORD_LENGTH = 8
    MAX_PASSWORD_LENGTH = 128
    REQUIRE_SPECIAL_CHARS = True
    
    # Rate limiting for auth endpoints
    LOGIN_RATE_LIMIT = "5/minute"
    REGISTER_RATE_LIMIT = "3/minute"
    
    # Session configuration
    MAX_ACTIVE_SESSIONS_PER_USER = 5


# =============================================================================
# Business Logic Limits
# =============================================================================

class BusinessLimits:
    """Business rules and validation constants"""
    
    # User limits
    MAX_POLLS_PER_USER = 100
    MAX_VOTES_PER_USER_PER_DAY = 1000
    
    # Poll limits
    MIN_POLL_TITLE_LENGTH = 5
    MAX_POLL_TITLE_LENGTH = 200
    MAX_POLL_DESCRIPTION_LENGTH = 1000
    MIN_POLL_OPTIONS = 2
    MAX_POLL_OPTIONS = 10
    MAX_POLL_OPTION_LENGTH = 100  # Individual option text length
    MAX_OPTION_TEXT_LENGTH = 100  # Keep for backward compatibility
    
    # Rate limits for poll operations
    POLL_CREATION_RATE_LIMIT = "5/hour"
    VOTING_RATE_LIMIT = "10/minute"
    
    # User profile limits
    MIN_USERNAME_LENGTH = 3
    MAX_USERNAME_LENGTH = 50
    MAX_FULL_NAME_LENGTH = 100


# =============================================================================
# Error Messages
# =============================================================================

class ErrorMessages:
    """Standardized error messages"""
    
    # Authentication errors
    AUTH_REQUIRED = "Authentication required"
    INVALID_CREDENTIALS = "Email o contraseña incorrectos"
    TOKEN_EXPIRED = "Token has expired"
    INVALID_TOKEN = "Invalid token"
    
    # Authorization errors
    NOT_AUTHORIZED_UPDATE = "Not authorized to update this poll"
    NOT_AUTHORIZED_DELETE = "Not authorized to delete this poll"
    NOT_AUTHORIZED_ADD_OPTIONS = "Not authorized to add options to this poll"
    NOT_AUTHORIZED_VIEW = "Not authorized to view this resource"
    
    # Resource errors
    POLL_NOT_FOUND = "Poll not found"
    USER_NOT_FOUND = "User not found"
    POLL_OPTION_NOT_FOUND = "Poll option not found"
    
    # Validation errors
    DUPLICATE_EMAIL = "Email already registered"
    DUPLICATE_USERNAME = "Username already registered"
    DUPLICATE_POLL_TITLE = "A poll with this title already exists"
    
    # Business rule violations
    POLL_LIMIT_EXCEEDED = "Maximum number of polls per user exceeded"
    RATE_LIMIT_EXCEEDED = "Rate limit exceeded"
    POLL_INACTIVE = "Poll is not active"
    ALREADY_VOTED = "User has already voted on this poll"
    
    # System errors
    DATABASE_ERROR = "Database operation failed"
    INTERNAL_ERROR = "An unexpected error occurred"
    VALIDATION_ERROR = "Validation failed"


# =============================================================================
# Error Codes
# =============================================================================

class ErrorCodes:
    """Standardized error codes for API responses"""
    
    # Authentication & Authorization
    AUTH_ERROR = "AUTH_ERROR"
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    INSUFFICIENT_PERMISSIONS = "INSUFFICIENT_PERMISSIONS"
    
    # Validation
    VALIDATION_ERROR = "VALIDATION_ERROR"
    MISSING_FIELD = "MISSING_FIELD"
    INVALID_FORMAT = "INVALID_FORMAT"
    
    # Business Logic
    DUPLICATE_RESOURCE = "DUPLICATE_RESOURCE"
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    BUSINESS_RULE_VIOLATION = "BUSINESS_RULE_VIOLATION"
    
    # System
    DATABASE_ERROR = "DATABASE_ERROR"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"


# =============================================================================
# Database Configuration
# =============================================================================

class DatabaseConfig:
    """Database-related constants"""
    
    # Connection settings
    POOL_SIZE = 5
    MAX_OVERFLOW = 10
    POOL_TIMEOUT = 30
    POOL_RECYCLE = 3600  # 1 hour
    
    # Query limits
    DEFAULT_PAGE_SIZE = 10
    MAX_PAGE_SIZE = 100
    MAX_QUERY_TIMEOUT = 30


# =============================================================================
# Logging Configuration
# =============================================================================

class LoggingConfig:
    """Logging configuration constants"""
    
    # Log levels
    DEFAULT_LOG_LEVEL = "INFO"
    DATABASE_LOG_LEVEL = "WARNING"
    
    # Log formats
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
    
    # File settings
    MAX_LOG_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    BACKUP_COUNT = 5


# =============================================================================
# Environment-Specific Constants
# =============================================================================

class EnvironmentConfig:
    """Environment-specific configuration"""
    
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"
    
    # Debug settings
    DEBUG_ENVIRONMENTS = [DEVELOPMENT, TESTING]
    
    # Features flags
    ENABLE_SWAGGER_IN_PRODUCTION = False
    ENABLE_METRICS_ENDPOINT = True


# =============================================================================
# Convenience Exports
# =============================================================================

# For backward compatibility and easy imports
API_V1_PREFIX = APIConfig.API_V1_PREFIX
MAX_POLLS_PER_USER = BusinessLimits.MAX_POLLS_PER_USER
ACCESS_TOKEN_EXPIRE_MINUTES = AuthConfig.ACCESS_TOKEN_EXPIRE_MINUTES

# Error messages (most commonly used)
POLL_NOT_FOUND = ErrorMessages.POLL_NOT_FOUND
NOT_AUTHORIZED_UPDATE = ErrorMessages.NOT_AUTHORIZED_UPDATE
NOT_AUTHORIZED_DELETE = ErrorMessages.NOT_AUTHORIZED_DELETE
NOT_AUTHORIZED_ADD_OPTIONS = ErrorMessages.NOT_AUTHORIZED_ADD_OPTIONS