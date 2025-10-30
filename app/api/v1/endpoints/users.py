from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from pydantic import BaseModel, ValidationError
from typing import Optional
import logging

from app.db.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserRead
from app.core.security import get_password_hash
from app.core.constants import ErrorMessages, ErrorCodes
from app.api.v1.endpoints.dependencies import get_current_user
from app.api.v1.responses import (
    get_user_creation_responses,
    get_user_profile_responses,
    get_user_update_responses
)

# Setup logging
logger = logging.getLogger(__name__)

# Constants for paths to avoid duplication
USERS_CREATE_PATH = "/api/v1/users/"
USERS_PROFILE_PATH = "/api/v1/users/me"

# Schema for user profile updates
class UserUpdate(BaseModel):
    """Schema for updating user profile information."""
    email: Optional[str] = None
    full_name: Optional[str] = None
    username: Optional[str] = None
    is_active: Optional[bool] = None


router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED, responses=get_user_creation_responses())
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user with comprehensive validation and error handling.
    
    Note: This endpoint creates users directly. For standard user registration,
    use the /auth/register endpoint instead.
    """
    try:
        # Enhanced logging with context
        logger.info(f"User creation attempt for email: {user.email}, username: {user.username}")
        
        # Check if the user already exists by email
        existing_email = db.query(User).filter(User.email == user.email).first()
        if existing_email:
            logger.warning(f"User creation failed: Email '{user.email}' already exists")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": ErrorMessages.DUPLICATE_EMAIL,
                    "error_code": ErrorCodes.DUPLICATE_RESOURCE,
                    "email": user.email,
                    "timestamp": "",
                    "path": USERS_CREATE_PATH
                }
            )
        
        # Check if username already exists
        existing_username = db.query(User).filter(User.username == user.username).first()
        if existing_username:
            logger.warning(f"User creation failed: Username '{user.username}' already exists")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": ErrorMessages.DUPLICATE_USERNAME,
                    "error_code": ErrorCodes.DUPLICATE_RESOURCE,
                    "username": user.username,
                    "timestamp": "",
                    "path": USERS_CREATE_PATH
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
        
        logger.info(f"User created successfully: ID {db_user.id}, email: {db_user.email}")
        return db_user
        
    except HTTPException:
        # Re-raise properly formatted HTTP errors
        raise
    except ValidationError as e:
        # Handle Pydantic validation errors
        logger.error(f"Validation error during user creation: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "message": ErrorMessages.VALIDATION_ERROR,
                "error_code": ErrorCodes.VALIDATION_ERROR,
                "errors": e.errors(),
                "timestamp": "",
                "path": USERS_CREATE_PATH
            }
        )
    except IntegrityError as e:
        # Handle database constraint violations
        db.rollback()
        logger.error(f"Database integrity error during user creation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "User creation failed due to data constraint violation",
                "error_code": ErrorCodes.DUPLICATE_RESOURCE,
                "timestamp": "",
                "path": USERS_CREATE_PATH
            }
        )
    except SQLAlchemyError as e:
        # Handle database errors
        db.rollback()
        logger.error(f"Database error during user creation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": ErrorMessages.DATABASE_ERROR,
                "error_code": ErrorCodes.DATABASE_ERROR,
                "timestamp": "",
                "path": USERS_CREATE_PATH
            }
        )
    except Exception as e:
        # Catch-all for unexpected errors
        db.rollback()
        logger.error(f"Unexpected error during user creation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": ErrorMessages.INTERNAL_ERROR,
                "error_code": ErrorCodes.INTERNAL_ERROR,
                "timestamp": "",
                "path": USERS_CREATE_PATH
            }
        )

# Example endpoint to get current user info (using dependency)
@router.get("/me", response_model=UserRead, responses=get_user_profile_responses())
def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Get current user profile information.
    
    Returns the profile information for the currently authenticated user.
    """
    try:
        logger.info(f"Profile retrieval for user ID: {current_user.id}")
        return current_user
    except Exception as e:
        logger.error(f"Unexpected error retrieving user profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": ErrorMessages.INTERNAL_ERROR,
                "error_code": ErrorCodes.INTERNAL_ERROR,
                "timestamp": "",
                "path": USERS_PROFILE_PATH
            }
        )

@router.put("/me", response_model=UserRead, responses=get_user_update_responses())
def update_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update current user profile information with change detection and validation.
    
    Only updates fields that are provided and different from current values.
    Provides comprehensive error handling and validation.
    """
    try:
        # Enhanced logging with context
        logger.info(f"Profile update attempt for user ID: {current_user.id}")
        
        # Get update data and exclude unset fields
        update_data = user_update.model_dump(exclude_unset=True)
        
        if not update_data:
            logger.info(f"No update data provided for user {current_user.id}")
            return current_user
        
        # Track changes for better logging and performance
        changes_made = False
        changed_fields = []
        
        # Check for duplicate email if email is being updated
        if 'email' in update_data and update_data['email'] is not None:
            new_email = update_data['email'].strip() if isinstance(update_data['email'], str) else update_data['email']
            if new_email != current_user.email:
                existing_email = db.query(User).filter(
                    User.email == new_email,
                    User.id != current_user.id  # Exclude current user
                ).first()
                
                if existing_email:
                    logger.warning(f"Profile update failed: Email '{new_email}' already exists for another user")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail={
                            "message": ErrorMessages.DUPLICATE_EMAIL,
                            "error_code": ErrorCodes.DUPLICATE_RESOURCE,
                            "email": new_email,
                            "timestamp": "",
                            "path": USERS_PROFILE_PATH
                        }
                    )
        
        # Check for duplicate username if username is being updated
        if 'username' in update_data and update_data['username'] is not None:
            new_username = update_data['username'].strip() if isinstance(update_data['username'], str) else update_data['username']
            if new_username != current_user.username:
                existing_username = db.query(User).filter(
                    User.username == new_username,
                    User.id != current_user.id  # Exclude current user
                ).first()
                
                if existing_username:
                    logger.warning(f"Profile update failed: Username '{new_username}' already exists")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail={
                            "message": ErrorMessages.DUPLICATE_USERNAME,
                            "error_code": ErrorCodes.DUPLICATE_RESOURCE,
                            "username": new_username,
                            "timestamp": "",
                            "path": USERS_PROFILE_PATH
                        }
                    )
        
        # Apply changes with change detection
        for field, new_value in update_data.items():
            current_value = getattr(current_user, field)
            
            # Handle string fields with proper comparison (strip whitespace)
            if field in ['email', 'username', 'full_name'] and isinstance(new_value, str):
                new_value = new_value.strip()
                current_value = current_value.strip() if current_value else None
            
            # Only update if the value is actually different
            if current_value != new_value:
                setattr(current_user, field, new_value)
                changes_made = True
                changed_fields.append(field)
        
        # Only commit if actual changes were made
        if changes_made:
            db.commit()
            db.refresh(current_user)
            logger.info(f"User profile updated successfully: ID {current_user.id}, Changed fields: {changed_fields}")
        else:
            logger.info(f"No changes detected for user {current_user.id} - all provided values match current values")
        
        return current_user
        
    except HTTPException:
        # Re-raise properly formatted HTTP errors
        raise
    except ValidationError as e:
        # Handle Pydantic validation errors
        logger.error(f"Validation error during profile update: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "message": ErrorMessages.VALIDATION_ERROR,
                "error_code": ErrorCodes.VALIDATION_ERROR,
                "errors": e.errors(),
                "timestamp": "",
                "path": USERS_PROFILE_PATH
            }
        )
    except IntegrityError as e:
        # Handle database constraint violations
        db.rollback()
        logger.error(f"Database integrity error during profile update: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Profile update failed due to data constraint violation",
                "error_code": ErrorCodes.DUPLICATE_RESOURCE,
                "timestamp": "",
                "path": USERS_PROFILE_PATH
            }
        )
    except SQLAlchemyError as e:
        # Handle database errors
        db.rollback()
        logger.error(f"Database error during profile update: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": ErrorMessages.DATABASE_ERROR,
                "error_code": ErrorCodes.DATABASE_ERROR,
                "timestamp": "",
                "path": USERS_PROFILE_PATH
            }
        )
    except Exception as e:
        # Catch-all for unexpected errors
        db.rollback()
        logger.error(f"Unexpected error during profile update: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": ErrorMessages.INTERNAL_ERROR,
                "error_code": ErrorCodes.INTERNAL_ERROR,
                "timestamp": "",
                "path": USERS_PROFILE_PATH
            }
        )