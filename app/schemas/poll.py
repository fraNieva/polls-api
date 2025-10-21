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
    title: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None