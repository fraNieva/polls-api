from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# Schema for creating a new poll
class PollCreate(BaseModel):
    title: str
    description: Optional[str] = None
    status: str = "active"

# Schema for reading poll data
class PollRead(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    status: str
    owner_id: int
    pub_date: datetime
    
    class Config:
        from_attributes = True

# Schema for updating a poll
class PollUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None