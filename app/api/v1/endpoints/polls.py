from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

from app.db.database import get_db
from app.models.polls import Poll
from app.models.user import User
from app.schemas.poll import PollCreate, PollRead, PollUpdate
from app.api.v1.endpoints.dependencies import get_current_user

router = APIRouter(prefix="/polls", tags=["polls"])

@router.post("/", response_model=PollRead, status_code=status.HTTP_201_CREATED)
def create_poll(
    poll: PollCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """Create a new poll. The current authenticated user becomes the owner."""
    db_poll = Poll(
        title=poll.title,
        description=poll.description,
        is_active=poll.is_active,
        owner_id=current_user.id  # Link to current user
        # pub_date will be auto-set by the model default
    )
    db.add(db_poll)
    db.commit()
    db.refresh(db_poll)
    return db_poll

@router.get("/", response_model=List[PollRead])
def get_polls(db: Session = Depends(get_db)):
    """Get all polls."""
    polls = db.query(Poll).all()
    return polls

@router.get("/my-polls", response_model=List[PollRead])
def get_my_polls(
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """Get all polls owned by the current user."""
    polls = db.query(Poll).filter(Poll.owner_id == current_user.id).all()
    return polls

@router.get("/{poll_id}", response_model=PollRead)
def get_poll(poll_id: int, db: Session = Depends(get_db)):
    """Get a specific poll by ID."""
    poll = db.query(Poll).filter(Poll.id == poll_id).first()
    if not poll:
        raise HTTPException(status_code=404, detail="Poll not found")
    return poll

@router.put("/{poll_id}", response_model=PollRead)
def update_poll(
    poll_id: int,
    poll_update: PollUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a poll. Only the owner can update their polls."""
    poll = db.query(Poll).filter(Poll.id == poll_id).first()
    if not poll:
        raise HTTPException(status_code=404, detail="Poll not found")
    
    # Check if the current user is the owner
    if poll.owner_id != current_user.id:
        raise HTTPException(
            status_code=403, 
            detail="Not authorized to update this poll"
        )
    
    # Update fields that were provided
    update_data = poll_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(poll, field, value)
    
    db.commit()
    db.refresh(poll)
    return poll

@router.delete("/{poll_id}")
def delete_poll(
    poll_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a poll. Only the owner can delete their polls."""
    poll = db.query(Poll).filter(Poll.id == poll_id).first()
    if not poll:
        raise HTTPException(status_code=404, detail="Poll not found")
    
    # Check if the current user is the owner
    if poll.owner_id != current_user.id:
        raise HTTPException(
            status_code=403, 
            detail="Not authorized to delete this poll"
        )
    
    db.delete(poll)
    db.commit()
    return {"message": "Poll deleted successfully"}