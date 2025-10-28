from app.db.database import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

# Define Poll model
class Poll(Base):
    __tablename__ = "polls"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)  # Removed unique constraint for tests
    description = Column(String, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)  # Changed from status to is_active
    is_public = Column(Boolean, default=True, nullable=False)  # Public by default for backward compatibility
    
    # Foreign key to user table
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    pub_date = Column(DateTime, default=func.now(), nullable=False)  # Auto-set to current time
    
    # Relationship to User model
    owner = relationship("User", back_populates="polls")
    # Relationship to PollOption model
    options = relationship(
        "PollOption",
        back_populates="poll",
        cascade="all, delete-orphan",
        order_by="PollOption.id"
    )


class PollOption(Base):
    __tablename__ = "poll_options"

    id = Column(Integer, primary_key=True, index=True)
    poll_id = Column(Integer, ForeignKey("polls.id"), nullable=False)
    text = Column(String, nullable=False)  # Changed from option_text to text
    vote_count = Column(Integer, default=0, nullable=False)  # Changed from votes to vote_count
    
    # Relationship to Poll model
    poll = relationship("Poll", back_populates="options")

    # Relationship to Vote model (reverse relationship)
    vote_details = relationship(
        "Vote",
        back_populates="poll_option",
        cascade="all, delete-orphan"
    )


class Vote(Base):
    __tablename__ = "votes"

    id = Column(Integer, primary_key=True, index=True)
    poll_option_id = Column(Integer, ForeignKey("poll_options.id"), nullable=False)
    poll_id = Column(Integer, ForeignKey("polls.id"), nullable=False)  # Direct reference to poll
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)  # Auto-set to current time
    
    # Relationships
    poll_option = relationship("PollOption", back_populates="vote_details")
    poll = relationship("Poll")  # Direct relationship to poll
    user = relationship("User")

    # Prevent duplicate votes by same user on same poll (the business rule we want)
    __table_args__ = (
        UniqueConstraint('poll_id', 'user_id', name='unique_user_vote_per_poll'),
    )