from pydantic import BaseModel, Field, field_validator, model_validator
from datetime import datetime
from typing import Optional, List
import re
from app.core.constants import BusinessLimits

# Schema for creating a new poll
class PollCreate(BaseModel):
    title: str = Field(
        ...,
        min_length=BusinessLimits.MIN_POLL_TITLE_LENGTH,
        max_length=BusinessLimits.MAX_POLL_TITLE_LENGTH,
        description=f'Poll title ({BusinessLimits.MIN_POLL_TITLE_LENGTH}-{BusinessLimits.MAX_POLL_TITLE_LENGTH} characters)',
        example="What's yout favourite programming language?"
    )
    description: Optional[str] = Field(
        None,
        max_length=BusinessLimits.MAX_POLL_DESCRIPTION_LENGTH,
        description=f'Optional poll description (max {BusinessLimits.MAX_POLL_DESCRIPTION_LENGTH} characters)',
        example="Vote for your preferred programming language for web development"
    )
    is_active: bool = Field(
        True,
        description="Whether the poll is active and acceptiong votes"
    )

    @field_validator('title')
    def validate_title(cls, v):
        if not v or not v.strip():
            raise ValueError('Title cannot be empty or just whitespace')
        
        # Remove excessive whitespace
        v = ' '.join(v.split())
        
        # Check for inappropriate content (basic example)
        forbidden_words = ['spam', 'test123', 'abuse']
        if any(word.lower() in v.lower() for word in forbidden_words):
            raise ValueError('Title contains inappropriate content')
        
        # Must contain at least one letter
        if not re.search(r'[a-zA-Z]', v):
            raise ValueError('Title must contain at least one letter')
            
        return v
        
    @field_validator('description')
    def validate_description(cls, v):
        if v is not None:
            # Remove excessive whitespace
            v = ' '.join(v.split()) if v.strip() else None
            
        return v
        
    @model_validator(mode='before')
    def validate_poll_data(cls, values):
        if isinstance(values, dict):
            title = values.get('title', '')
            description = values.get('description', '')
            
            # Title and description cannot be identical
            if title and description and title.lower().strip() == description.lower().strip():
                raise ValueError('Title and description cannot be identical')
        
        return values
    
class PollCreateWithOptions(PollCreate):
    """Enhanced schema for creating polls with initial options"""
    options: List[str] = Field(
        [],
        min_items=0,
        max_items=10,
        description="Initial poll options (0-10 options, can be added later)"
    )
    
    @field_validator('options')
    def validate_options(cls, v):
        if not v:
            return v
            
        # Remove duplicates while preserving order
        seen = set()
        unique_options = []
        for option in v:
            option = option.strip()
            if option and option.lower() not in seen:
                seen.add(option.lower())
                unique_options.append(option)
        
        if len(unique_options) < 2 and len(unique_options) > 0:
            raise ValueError('If providing options, must provide at least 2 unique options')
            
        # Validate each option
        for option in unique_options:
            if len(option) < 1 or len(option) > 100:
                raise ValueError('Each option must be 1-100 characters long')
                
        return unique_options

# Schema for reading poll data
class PollRead(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    is_active: bool
    owner_id: int
    pub_date: datetime
    
    class Config:
        from_attributes = True

# Schema for updating a poll
class PollUpdate(BaseModel):
    title: Optional[str] = Field(
        None,
        min_length=BusinessLimits.MIN_POLL_TITLE_LENGTH,
        max_length=BusinessLimits.MAX_POLL_TITLE_LENGTH,
        description=f'Poll title ({BusinessLimits.MIN_POLL_TITLE_LENGTH}-{BusinessLimits.MAX_POLL_TITLE_LENGTH} characters)',
    )
    description: Optional[str] = Field(
        None,
        max_length=BusinessLimits.MAX_POLL_DESCRIPTION_LENGTH,
        description=f'Optional poll description (max {BusinessLimits.MAX_POLL_DESCRIPTION_LENGTH} characters)',
    )
    is_active: Optional[bool] = None

    @field_validator('title')
    def validate_title(cls, v):
        # Skip validation if field is not being updated (None)
        if v is None:
            return v
            
        if not v or not v.strip():
            raise ValueError('Title cannot be empty or just whitespace')
        
        # Remove excessive whitespace
        v = ' '.join(v.split())
        
        # Check for inappropriate content (basic example)
        forbidden_words = ['spam', 'test123', 'abuse']
        if any(word.lower() in v.lower() for word in forbidden_words):
            raise ValueError('Title contains inappropriate content')
        
        # Must contain at least one letter
        if not re.search(r'[a-zA-Z]', v):
            raise ValueError('Title must contain at least one letter')
            
        return v
        
    @field_validator('description')
    def validate_description(cls, v):
        # Skip validation if field is not being updated (None)
        if v is None:
            return v
            
        # Remove excessive whitespace
        v = ' '.join(v.split()) if v.strip() else None
        return v


# Enhanced response schemas for paginated endpoints
class PaginationMeta(BaseModel):
    """Pagination metadata for responses"""
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Items per page")
    pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there are more pages")
    has_prev: bool = Field(..., description="Whether there are previous pages")

    class Config:
        schema_extra = {
            "example": {
                "total": 25,
                "page": 2,
                "size": 10,
                "pages": 3,
                "has_next": True,
                "has_prev": True
            }
        }


class PaginatedPollResponse(BaseModel):
    """Paginated response for poll listings"""
    polls: List[PollRead] = Field(..., description="List of polls for current page")
    total: int = Field(..., description="Total number of polls")
    page: int = Field(..., description="Current page number") 
    size: int = Field(..., description="Items per page")
    pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there are more pages")
    has_prev: bool = Field(..., description="Whether there are previous pages")

    class Config:
        schema_extra = {
            "example": {
                "polls": [
                    {
                        "id": 1,
                        "title": "Favorite Programming Language",
                        "description": "What's your favorite programming language?",
                        "is_active": True,
                        "created_at": "2023-12-01T10:00:00Z",
                        "updated_at": "2023-12-01T10:00:00Z",
                        "owner_id": 1,
                        "options": [
                            {"id": 1, "text": "Python", "vote_count": 5},
                            {"id": 2, "text": "JavaScript", "vote_count": 3}
                        ]
                    }
                ],
                "total": 25,
                "page": 1,
                "size": 10,
                "pages": 3,
                "has_next": True,
                "has_prev": False
            }
        }