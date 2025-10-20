from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.db.database import Base

# Define the User model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    
    # Relationship to Poll model (one user can have many polls)
    polls = relationship("Poll", back_populates="owner", cascade="all, delete-orphan")
    # Relationship to Vote model (one user can have many votes)
    votes = relationship("Vote", back_populates="user", cascade="all, delete-orphan")