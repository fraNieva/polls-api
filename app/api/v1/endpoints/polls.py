from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy import func
from pydantic import ValidationError
from datetime import datetime, timezone
from typing import List, Optional
from enum import Enum
import math

from app.db.database import get_db
from app.models.polls import Poll, Vote, PollOption
from app.models.user import User
from app.schemas.poll import PollCreate, PollRead, PollUpdate, PaginatedPollResponse
from app.schemas.common import PaginatedResponse
from app.api.v1.endpoints.dependencies import get_current_user
from app.core.constants import DatabaseConfig
from app.api.v1.utils.pagination import (
    PaginationParams, 
    get_pagination_params,
    create_paginated_response,
    apply_search,
    paginate_query
)

from app.schemas.error import (
    ValidationErrorResponse, 
    BusinessErrorResponse, 
    AuthErrorResponse,
    RateLimitErrorResponse,
    ServerErrorResponse
)

from app.core.constants import (
    ErrorMessages, 
    BusinessLimits, 
    ErrorCodes
)

import logging

# Set up logging
logger = logging.getLogger(__name__)

# Define sort options enum for validation
class SortOption(str, Enum):
    CREATED_DESC = "created_desc"
    CREATED_ASC = "created_asc" 
    TITLE_ASC = "title_asc"
    TITLE_DESC = "title_desc"
    VOTES_DESC = "votes_desc"
    VOTES_ASC = "votes_asc"

router = APIRouter(prefix="/polls", tags=["polls"])

@router.post(
    "/",
    response_model=PollRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new poll",
    description="Create a new poll. The authenticated user becomes the owner. Optionally include initial options.",
    responses={
        201: {
            "description": "Poll created successfully",
            "model": PollRead,
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "title": "Favorite Programming Language",
                        "description": "Vote for your preferred language",
                        "is_active": True,
                        "owner_id": 1,
                        "pub_date": "2024-01-01T12:00:00Z",
                        "options": []
                    }
                }
            }
        },
        400: {
            "description": "Business logic error",
            "model": BusinessErrorResponse,
            "content": {
                "application/json": {
                    "examples": {
                        "duplicate_poll": {
                            "summary": "Duplicate poll title",
                            "value": {
                                "message": "A poll with this title already exists",
                                "error_code": "DUPLICATE_POLL_TITLE",
                                "details": {"existing_poll_id": 123},
                                "timestamp": "2024-01-01T12:00:00Z",
                                "path": "/api/v1/polls/"
                            }
                        },
                        "poll_limit": {
                            "summary": "Poll creation limit exceeded",
                            "value": {
                                "message": "Maximum number of polls per user exceeded (100)",
                                "error_code": "POLL_LIMIT_EXCEEDED",
                                "details": {
                                    "current_count": 100,
                                    "max_allowed": 100
                                },
                                "timestamp": "2024-01-01T12:00:00Z",
                                "path": "/api/v1/polls/"
                            }
                        }
                    }
                }
            }
        },
        401: {
            "description": "Authentication required",
            "model": AuthErrorResponse
        },
        422: {
            "description": "Validation error",
            "model": ValidationErrorResponse,
            "content": {
                "application/json": {
                    "example": {
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
                        "timestamp": "2024-01-01T12:00:00Z",
                        "path": "/api/v1/polls/"
                    }
                }
            }
        },
        429: {
            "description": "Rate limit exceeded",
            "model": RateLimitErrorResponse
        },
        500: {
            "description": "Internal server error",
            "model": ServerErrorResponse
        }
    }
)
def create_poll(
    poll: PollCreate, 
    request: Request,
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """Create a new poll with comprehensive validation and error handling."""
    
    try:
        # Log poll creation attempt
        logger.info(f"User {current_user.id} attempting to create poll: '{poll.title}'")
        
        # Additional business logic validation
        _validate_poll_business_rules(poll, current_user, db)
        
        # Check for duplicate titles by this user
        existing_poll = db.query(Poll).filter(
            Poll.title == poll.title.strip(),
            Poll.owner_id == current_user.id
        ).first()
        
        if existing_poll:
            logger.warning(f"User {current_user.id} attempted to create duplicate poll: '{poll.title}'")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "message": "A poll with this title already exists",
                    "error_code": "DUPLICATE_POLL_TITLE",
                    "existing_poll_id": existing_poll.id
                }
            )
        
        # Create the poll
        db_poll = Poll(
            title=poll.title.strip(),
            description=poll.description.strip() if poll.description else None,
            is_active=poll.is_active,
            owner_id=current_user.id
        )
        
        db.add(db_poll)
        db.commit()
        db.refresh(db_poll)
        
        logger.info(f"Poll created successfully: ID {db_poll.id}, Title: '{db_poll.title}'")
        
        return db_poll
        
    except HTTPException:
        # Re-raise HTTP exceptions (they're already properly formatted)
        raise
        
    except ValidationError as e:
        logger.error(f"Validation error creating poll: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "message": "Validation failed",
                "error_code": "VALIDATION_ERROR",
                "errors": e.errors()
            }
        )
        
    except IntegrityError as e:
        logger.error(f"Database integrity error creating poll: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Data integrity constraint violated",
                "error_code": "INTEGRITY_ERROR",
                "hint": "Check for duplicate values or invalid references"
            }
        )
        
    except SQLAlchemyError as e:
        logger.error(f"Database error creating poll: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Database operation failed",
                "error_code": "DATABASE_ERROR"
            }
        )
        
    except Exception as e:
        logger.error(f"Unexpected error creating poll: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "An unexpected error occurred",
                "error_code": "INTERNAL_ERROR"
            }
        )

def _validate_poll_business_rules(poll: PollCreate, current_user: User, db: Session):
    """Additional business logic validation"""
    
    # Check user poll creation limits
    user_poll_count = db.query(Poll).filter(Poll.owner_id == current_user.id).count()
    
    if user_poll_count >= BusinessLimits.MAX_POLLS_PER_USER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Maximum number of polls per user exceeded ({BusinessLimits.MAX_POLLS_PER_USER})",
                "error_code": ErrorCodes.BUSINESS_RULE_VIOLATION,
                "current_count": user_poll_count,
                "max_allowed": BusinessLimits.MAX_POLLS_PER_USER
            }
        )
    
    # Check for rate limiting (example: max 5 polls per hour)
    from datetime import datetime, timedelta
    one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
    recent_polls = db.query(Poll).filter(
        Poll.owner_id == current_user.id,
        Poll.pub_date >= one_hour_ago
    ).count()
    
    if recent_polls >= 5:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "message": "Rate limit exceeded. Maximum 5 polls per hour.",
                "error_code": "RATE_LIMIT_EXCEEDED",
                "retry_after": "3600"
            }
        )

@router.get("/", response_model=PaginatedResponse[PollRead])
def get_polls(
    db: Session = Depends(get_db),
    pagination: PaginationParams = Depends(get_pagination_params),
    search: Optional[str] = Query(None, description="Search in poll titles"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    owner_id: Optional[int] = Query(None, description="Filter by owner ID"),
    sort: SortOption = Query(SortOption.CREATED_DESC, description="Sort order")
):
    """
    Get paginated list of polls with filtering and sorting options.
    
    - **page**: Page number (starts from 1)
    - **size**: Number of polls per page (1-100)
    - **search**: Search text in poll titles (case-insensitive)
    - **is_active**: Filter by poll active status
    - **owner_id**: Filter polls by specific owner
    - **sort**: Sort order options:
        - created_desc: Newest first (default)
        - created_asc: Oldest first
        - title_asc: Title A-Z
        - title_desc: Title Z-A
        - votes_desc: Most voted first
        - votes_asc: Least voted first
    """
    try:
        # Build base query
        query = db.query(Poll)
        
        # Apply filters
        if is_active is not None:
            query = query.filter(Poll.is_active == is_active)
            
        if owner_id is not None:
            query = query.filter(Poll.owner_id == owner_id)
        
        # Apply sorting
        if sort == SortOption.CREATED_ASC:
            query = query.order_by(Poll.pub_date.asc())
        elif sort == SortOption.TITLE_ASC:
            query = query.order_by(Poll.title.asc())
        elif sort == SortOption.TITLE_DESC:
            query = query.order_by(Poll.title.desc())
        elif sort == SortOption.VOTES_DESC:
            # Count total votes for each poll and sort by that
            subquery = (
                db.query(
                    PollOption.poll_id,
                    func.sum(PollOption.vote_count).label('total_votes')
                )
                .group_by(PollOption.poll_id)
                .subquery()
            )
            query = (
                query.outerjoin(subquery, Poll.id == subquery.c.poll_id)
                .order_by(func.coalesce(subquery.c.total_votes, 0).desc())
            )
        elif sort == SortOption.VOTES_ASC:
            # Count total votes for each poll and sort by that
            subquery = (
                db.query(
                    PollOption.poll_id,
                    func.sum(PollOption.vote_count).label('total_votes')
                )
                .group_by(PollOption.poll_id)
                .subquery()
            )
            query = (
                query.outerjoin(subquery, Poll.id == subquery.c.poll_id)
                .order_by(func.coalesce(subquery.c.total_votes, 0).asc())
            )
        else:  # Default: CREATED_DESC
            query = query.order_by(Poll.pub_date.desc())
        
        # Apply pagination and search using utilities
        polls, total = paginate_query(
            query,
            pagination,
            search_term=search,
            search_fields=[Poll.title] if search else None
        )
        
        # Create paginated response using utility
        return create_paginated_response(polls, total, pagination)
        
    except Exception as e:
        logger.error(f"Error retrieving polls: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": ErrorMessages.INTERNAL_ERROR,
                "error_code": "POLL_RETRIEVAL_FAILED"
            }
        )


@router.get("/my-polls", response_model=PaginatedResponse[PollRead])
def get_my_polls(
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user),
    pagination: PaginationParams = Depends(get_pagination_params),
    search: Optional[str] = Query(None, description="Search in poll titles"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    sort: SortOption = Query(SortOption.CREATED_DESC, description="Sort order")
):
    """
    Get paginated list of polls owned by the current user.
    
    - **page**: Page number (starts from 1)
    - **size**: Number of polls per page (1-100)
    - **search**: Search text in poll titles (case-insensitive)
    - **is_active**: Filter by poll active status
    - **sort**: Sort order options:
        - created_desc: Newest first (default)
        - created_asc: Oldest first
        - title_asc: Title A-Z
        - title_desc: Title Z-A
        - votes_desc: Most voted first
        - votes_asc: Least voted first
    """
    try:
        # Build base query for user's polls
        query = db.query(Poll).filter(Poll.owner_id == current_user.id)
        
        # Apply filters
        if is_active is not None:
            query = query.filter(Poll.is_active == is_active)
        
        # Apply sorting
        if sort == SortOption.CREATED_ASC:
            query = query.order_by(Poll.pub_date.asc())
        elif sort == SortOption.TITLE_ASC:
            query = query.order_by(Poll.title.asc())
        elif sort == SortOption.TITLE_DESC:
            query = query.order_by(Poll.title.desc())
        elif sort == SortOption.VOTES_DESC:
            # Count total votes for each poll and sort by that
            subquery = (
                db.query(
                    PollOption.poll_id,
                    func.sum(PollOption.vote_count).label('total_votes')
                )
                .group_by(PollOption.poll_id)
                .subquery()
            )
            query = (
                query.outerjoin(subquery, Poll.id == subquery.c.poll_id)
                .order_by(func.coalesce(subquery.c.total_votes, 0).desc())
            )
        elif sort == SortOption.VOTES_ASC:
            # Count total votes for each poll and sort by that
            subquery = (
                db.query(
                    PollOption.poll_id,
                    func.sum(PollOption.vote_count).label('total_votes')
                )
                .group_by(PollOption.poll_id)
                .subquery()
            )
            query = (
                query.outerjoin(subquery, Poll.id == subquery.c.poll_id)
                .order_by(func.coalesce(subquery.c.total_votes, 0).asc())
            )
        else:  # Default: CREATED_DESC
            query = query.order_by(Poll.pub_date.desc())
        
        # Apply pagination and search using utilities
        polls, total = paginate_query(
            query,
            pagination,
            search_term=search,
            search_fields=[Poll.title] if search else None
        )
        
        # Create paginated response using utility
        return create_paginated_response(polls, total, pagination)
        
    except Exception as e:
        logger.error(f"Error retrieving user polls: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": ErrorMessages.INTERNAL_ERROR,
                "error_code": "USER_POLLS_RETRIEVAL_FAILED"
            }
        )

@router.get("/{poll_id}", response_model=PollRead)
def get_poll(poll_id: int, db: Session = Depends(get_db)):
    """Get a specific poll by ID."""
    poll = db.query(Poll).filter(Poll.id == poll_id).first()
    if not poll:
        raise HTTPException(status_code=404, detail=ErrorMessages.POLL_NOT_FOUND)
    return poll

@router.put(
    "/{poll_id}", 
    response_model=PollRead,
    summary="Update an existing poll",
    description="Update a poll's title, description, or active status. Only the poll owner can update their polls.",
    responses={
        200: {
            "description": "Poll updated successfully",
            "model": PollRead,
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "title": "Updated Poll Title",
                        "description": "Updated description",
                        "is_active": True,
                        "owner_id": 1,
                        "pub_date": "2024-01-01T12:00:00Z"
                    }
                }
            }
        },
        400: {
            "description": "Business logic error",
            "model": BusinessErrorResponse,
            "content": {
                "application/json": {
                    "examples": {
                        "duplicate_title": {
                            "summary": "Duplicate poll title",
                            "value": {
                                "message": "A poll with this title already exists",
                                "error_code": "DUPLICATE_POLL_TITLE",
                                "details": {"existing_poll_id": 123, "poll_id": 1},
                                "timestamp": "2024-01-01T12:00:00Z",
                                "path": "/api/v1/polls/1"
                            }
                        },
                        "integrity_error": {
                            "summary": "Database integrity constraint violated",
                            "value": {
                                "message": "Data integrity constraint violated",
                                "error_code": "INTEGRITY_ERROR",
                                "hint": "Check for duplicate values or invalid references",
                                "poll_id": 1,
                                "timestamp": "2024-01-01T12:00:00Z",
                                "path": "/api/v1/polls/1"
                            }
                        }
                    }
                }
            }
        },
        401: {
            "description": "Authentication required",
            "model": AuthErrorResponse
        },
        403: {
            "description": "Access forbidden - not poll owner",
            "model": AuthErrorResponse,
            "content": {
                "application/json": {
                    "example": {
                        "message": "Not authorized to update this poll",
                        "error_code": "NOT_AUTHORIZED_UPDATE",
                        "poll_id": 1,
                        "owner_id": 2,
                        "timestamp": "2024-01-01T12:00:00Z",
                        "path": "/api/v1/polls/1"
                    }
                }
            }
        },
        404: {
            "description": "Poll not found",
            "model": BusinessErrorResponse,
            "content": {
                "application/json": {
                    "example": {
                        "message": "Poll not found",
                        "error_code": "POLL_NOT_FOUND",
                        "poll_id": 999,
                        "timestamp": "2024-01-01T12:00:00Z",
                        "path": "/api/v1/polls/999"
                    }
                }
            }
        },
        422: {
            "description": "Validation error",
            "model": ValidationErrorResponse,
            "content": {
                "application/json": {
                    "example": {
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
                        "poll_id": 1,
                        "timestamp": "2024-01-01T12:00:00Z",
                        "path": "/api/v1/polls/1"
                    }
                }
            }
        },
        500: {
            "description": "Internal server error",
            "model": ServerErrorResponse,
            "content": {
                "application/json": {
                    "example": {
                        "message": "An unexpected error occurred",
                        "error_code": "INTERNAL_ERROR",
                        "poll_id": 1,
                        "timestamp": "2024-01-01T12:00:00Z",
                        "path": "/api/v1/polls/1"
                    }
                }
            }
        }
    }
)
def update_poll(
    poll_id: int,
    poll_update: PollUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a poll. Only the owner can update their polls."""
    
    try:
        # Log poll update attempt
        logger.info(f"User {current_user.id} attempting to update poll ID: {poll_id}")
        
        # Get the poll
        poll = db.query(Poll).filter(Poll.id == poll_id).first()
        if not poll:
            logger.warning(f"Poll not found: ID {poll_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "message": ErrorMessages.POLL_NOT_FOUND,
                    "error_code": "POLL_NOT_FOUND",
                    "poll_id": poll_id
                }
            )
        
        # Check if the current user is the owner
        if poll.owner_id != current_user.id:
            logger.warning(f"User {current_user.id} attempted to update poll {poll_id} owned by user {poll.owner_id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "message": ErrorMessages.NOT_AUTHORIZED_UPDATE,
                    "error_code": "NOT_AUTHORIZED_UPDATE",
                    "poll_id": poll_id,
                    "owner_id": poll.owner_id
                }
            )
        
        # Check for duplicate titles only if title is being updated
        update_data = poll_update.model_dump(exclude_unset=True)
        if 'title' in update_data and update_data['title'] is not None:
            existing_poll = db.query(Poll).filter(
                Poll.title == update_data['title'].strip(),
                Poll.owner_id == current_user.id,
                Poll.id != poll_id  # Exclude the current poll from duplicate check
            ).first()
            
            if existing_poll:
                logger.warning(f"User {current_user.id} attempted to update poll {poll_id} with duplicate title: '{update_data['title']}'")
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail={
                        "message": "A poll with this title already exists",
                        "error_code": "DUPLICATE_POLL_TITLE",
                        "existing_poll_id": existing_poll.id,
                        "poll_id": poll_id
                    }
                )

        # Update fields that were provided
        if not update_data:
            logger.info(f"No fields to update for poll {poll_id}")
            return poll  # No changes requested
        
        for field, value in update_data.items():
            setattr(poll, field, value)
        
        db.commit()
        db.refresh(poll)
        
        logger.info(f"Poll updated successfully: ID {poll.id}, Fields: {list(update_data.keys())}")
        return poll
        
    except HTTPException:
        # Re-raise HTTP exceptions (they're already properly formatted)
        raise
        
    except ValidationError as e:
        logger.error(f"Validation error updating poll {poll_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "message": "Validation failed",
                "error_code": "VALIDATION_ERROR",
                "errors": e.errors(),
                "poll_id": poll_id
            }
        )
        
    except IntegrityError as e:
        logger.error(f"Database integrity error updating poll {poll_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Data integrity constraint violated",
                "error_code": "INTEGRITY_ERROR",
                "hint": "Check for duplicate values or invalid references",
                "poll_id": poll_id
            }
        )
        
    except SQLAlchemyError as e:
        logger.error(f"Database error updating poll {poll_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Database operation failed",
                "error_code": "DATABASE_ERROR",
                "poll_id": poll_id
            }
        )
        
    except Exception as e:
        logger.error(f"Unexpected error updating poll {poll_id}: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "An unexpected error occurred",
                "error_code": "INTERNAL_ERROR",
                "poll_id": poll_id
            }
        )

@router.delete("/{poll_id}")
def delete_poll(
    poll_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a poll. Only the owner can delete their polls."""
    poll = db.query(Poll).filter(Poll.id == poll_id).first()
    if not poll:
        raise HTTPException(status_code=404, detail=ErrorMessages.POLL_NOT_FOUND)
    
    # Check if the current user is the owner
    if poll.owner_id != current_user.id:
        raise HTTPException(
            status_code=403, 
            detail=ErrorMessages.NOT_AUTHORIZED_DELETE
        )
    
    db.delete(poll)
    db.commit()
    return {"message": "Poll deleted successfully"}

@router.post("/{poll_id}/options", status_code=status.HTTP_201_CREATED)
def add_poll_option(
    poll_id: int,
    option_text: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add an option to a poll. Only the poll owner can add options."""
    poll = db.query(Poll).filter(Poll.id == poll_id).first()
    if not poll:
        raise HTTPException(status_code=404, detail=ErrorMessages.POLL_NOT_FOUND)
    
    # Check if the current user is the owner
    if poll.owner_id != current_user.id:
        raise HTTPException(
            status_code=403, 
            detail=ErrorMessages.NOT_AUTHORIZED_ADD_OPTIONS
        )
    
    # Create the new option
    poll_option = PollOption(
        poll_id=poll_id,
        text=option_text
    )
    db.add(poll_option)
    db.commit()
    db.refresh(poll_option)
    
    return {"message": "Option added successfully", "option_id": poll_option.id, "text": option_text}

@router.post('/{poll_id}/vote/{option_id}', status_code=status.HTTP_200_OK)
def vote_poll(
    poll_id: int,
    option_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Vote on a specific poll option."""
    # Verify user is authenticated
    if not current_user:
        raise HTTPException(
            status_code=401,
            detail="Authentication required to vote"
        )
    
    # Get the poll
    poll = db.query(Poll).filter(Poll.id == poll_id).first()
    if not poll:
        raise HTTPException(status_code=404, detail=ErrorMessages.POLL_NOT_FOUND)
    
    # Verify if poll is active
    if not poll.is_active:
        raise HTTPException(
            status_code=403,
            detail="Poll is not active"
        )
    
    # Get the poll option
    poll_option = db.query(PollOption).filter(
        PollOption.id == option_id,
        PollOption.poll_id == poll_id
    ).first()
    if not poll_option:
        raise HTTPException(status_code=404, detail=ErrorMessages.POLL_OPTION_NOT_FOUND)
    
    # Check if user has already voted on this poll (any option)
    existing_vote = db.query(Vote).join(PollOption).filter(
        PollOption.poll_id == poll_id,
        Vote.user_id == current_user.id
    ).first()
    if existing_vote:
        raise HTTPException(
            status_code=403,
            detail="User has already voted on this poll"
        )
    
    # Record the vote
    vote = Vote(
        user_id=current_user.id,
        poll_option_id=option_id,
        poll_id=poll_id  # Set the poll_id directly
    )
    db.add(vote)
    
    # Increment the vote count for this option
    poll_option.vote_count += 1
    
    db.commit()
    db.refresh(poll_option)
    
    return {"message": "Vote recorded successfully", "poll_id": poll_id, "option_id": option_id}