from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from pydantic import BaseModel, ValidationError
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
import logging

from app.db.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserRead
from app.core.security import verify_password, create_access_token, get_password_hash
from app.core.security import ACCESS_TOKEN_EXPIRE_MINUTES
from app.core.constants import ErrorMessages, ErrorCodes, BusinessLimits
from app.api.v1.responses import (
    get_registration_responses,
    get_login_responses,
    get_token_responses
)

# Setup logging
logger = logging.getLogger(__name__)

# Constants for paths to avoid duplication
REGISTER_PATH = "/api/v1/auth/register"
LOGIN_PATH = "/api/v1/auth/login"
TOKEN_PATH = "/api/v1/auth/token"

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class LoginRequest(BaseModel):
    email: str
    password: str

# OAuth2 scheme for token-based authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED, responses=get_registration_responses())
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user with comprehensive validation and error handling.
    
    Creates a new user account with the provided information, including proper
    password hashing and duplicate validation.
    """
    try:
        # Enhanced logging with context
        logger.info(f"Registration attempt for email: {user.email}, username: {user.username}")
        
        # Business rule validation - could add rate limiting here
        # For now, we focus on duplicate validation
        
        # Check if username already exists
        existing_username = db.query(User).filter(User.username == user.username).first()
        if existing_username:
            logger.warning(f"Registration failed: Username '{user.username}' already exists")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail={
                    "message": ErrorMessages.DUPLICATE_USERNAME,
                    "error_code": ErrorCodes.DUPLICATE_RESOURCE,
                    "username": user.username,
                    "timestamp": "",  # Will be set by middleware
                    "path": REGISTER_PATH
                }
            )
        
        # Check if email already exists
        existing_email = db.query(User).filter(User.email == user.email).first()
        if existing_email:
            logger.warning(f"Registration failed: Email '{user.email}' already exists")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": ErrorMessages.DUPLICATE_EMAIL,
                    "error_code": ErrorCodes.DUPLICATE_RESOURCE,
                    "email": user.email,
                    "timestamp": "",  # Will be set by middleware
                    "path": REGISTER_PATH
                }
            )
        
        # Hash the password before storing it
        hashed_password = get_password_hash(user.password)
        
        # Create new user instance
        db_user = User(
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            hashed_password=hashed_password,
            is_active=user.is_active
        )
        
        # Save to database
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        logger.info(f"User registered successfully: ID {db_user.id}, email: {db_user.email}")
        return db_user
        
    except HTTPException:
        # Re-raise properly formatted HTTP errors
        raise
    except ValidationError as e:
        # Handle Pydantic validation errors
        logger.error(f"Validation error during registration: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "message": ErrorMessages.VALIDATION_ERROR,
                "error_code": ErrorCodes.VALIDATION_ERROR,
                "errors": e.errors(),
                "timestamp": "",
                "path": REGISTER_PATH
            }
        )
    except IntegrityError as e:
        # Handle database constraint violations
        db.rollback()
        logger.error(f"Database integrity error during registration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Registration failed due to data constraint violation",
                "error_code": ErrorCodes.DUPLICATE_RESOURCE,
                "timestamp": "",
                "path": REGISTER_PATH
            }
        )
    except SQLAlchemyError as e:
        # Handle database errors
        db.rollback()
        logger.error(f"Database error during registration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": ErrorMessages.DATABASE_ERROR,
                "error_code": ErrorCodes.DATABASE_ERROR,
                "timestamp": "",
                "path": REGISTER_PATH
            }
        )
    except Exception as e:
        # Catch-all for unexpected errors
        db.rollback()
        logger.error(f"Unexpected error during registration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": ErrorMessages.INTERNAL_ERROR,
                "error_code": ErrorCodes.INTERNAL_ERROR,
                "timestamp": "",
                "path": REGISTER_PATH
            }
        )

@router.post("/token", response_model=Token, responses=get_token_responses())
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return a JWT token. Uses OAuth2 compatible form data.
    
    IMPORTANT: In the 'username' field, enter the user's EMAIL ADDRESS, not their username!
    This endpoint is compatible with OAuth2 password flow and provides comprehensive error handling.
    """
    try:
        # Enhanced logging
        logger.info(f"OAuth2 token request for email: {form_data.username}")
        
        # Find user by email (note: OAuth2 uses 'username' field for email)
        user = db.query(User).filter(User.email == form_data.username).first()
        
        if not user or not verify_password(form_data.password, user.hashed_password):
            logger.warning(f"Failed login attempt for email: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "message": ErrorMessages.INVALID_CREDENTIALS,
                    "error_code": ErrorCodes.INVALID_CREDENTIALS,
                    "timestamp": "",
                    "path": TOKEN_PATH,
                    "hint": "Enter your EMAIL ADDRESS in the 'username' field, not your username"
                },
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        # Create the JWT token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email},  # 'sub' (subject) is the user's email.
            expires_delta=access_token_expires
        )
        
        logger.info(f"Token generated successfully for user: {user.email}")
        return {"access_token": access_token, "token_type": "bearer"}
        
    except HTTPException:
        # Re-raise properly formatted HTTP errors
        raise
    except SQLAlchemyError as e:
        # Handle database errors
        logger.error(f"Database error during token generation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": ErrorMessages.DATABASE_ERROR,
                "error_code": ErrorCodes.DATABASE_ERROR,
                "timestamp": "",
                "path": TOKEN_PATH
            }
        )
    except Exception as e:
        # Catch-all for unexpected errors
        logger.error(f"Unexpected error during token generation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": ErrorMessages.INTERNAL_ERROR,
                "error_code": ErrorCodes.INTERNAL_ERROR,
                "timestamp": "",
                "path": TOKEN_PATH
            }
        )

@router.post("/login", response_model=Token, responses=get_login_responses())
def simple_login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """
    Simple login endpoint - easier to use than OAuth2 form.
    
    Just provide email and password in JSON format with comprehensive error handling.
    """
    try:
        # Enhanced logging
        logger.info(f"Simple login attempt for email: {login_data.email}")
        
        # Find user by email
        user = db.query(User).filter(User.email == login_data.email).first()
        
        if not user or not verify_password(login_data.password, user.hashed_password):
            logger.warning(f"Failed login attempt for email: {login_data.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "message": ErrorMessages.INVALID_CREDENTIALS,
                    "error_code": ErrorCodes.INVALID_CREDENTIALS,
                    "timestamp": "",
                    "path": LOGIN_PATH
                }
            )
            
        # Create the JWT token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email},
            expires_delta=access_token_expires
        )
        
        logger.info(f"Login successful for user: {user.email}")
        return {"access_token": access_token, "token_type": "bearer"}
        
    except HTTPException:
        # Re-raise properly formatted HTTP errors
        raise
    except ValidationError as e:
        # Handle Pydantic validation errors
        logger.error(f"Validation error during login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "message": ErrorMessages.VALIDATION_ERROR,
                "error_code": ErrorCodes.VALIDATION_ERROR,
                "errors": e.errors(),
                "timestamp": "",
                "path": LOGIN_PATH
            }
        )
    except SQLAlchemyError as e:
        # Handle database errors
        logger.error(f"Database error during login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": ErrorMessages.DATABASE_ERROR,
                "error_code": ErrorCodes.DATABASE_ERROR,
                "timestamp": "",
                "path": LOGIN_PATH
            }
        )
    except Exception as e:
        # Catch-all for unexpected errors
        logger.error(f"Unexpected error during login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": ErrorMessages.INTERNAL_ERROR,
                "error_code": ErrorCodes.INTERNAL_ERROR,
                "timestamp": "",
                "path": LOGIN_PATH
            }
        )
