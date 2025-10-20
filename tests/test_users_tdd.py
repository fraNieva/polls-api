"""
Test-Driven Development tests for User functionality.

This follows TDD methodology:
1. Write failing tests first
2. Write minimal code to pass tests  
3. Refactor while keeping tests green
"""

import pytest
from sqlalchemy import text
from app.models.user import User
from app.core.security import hash_password, verify_password


def test_user_model_creation(db_session):
    """Test that we can create a User model instance"""
    # Arrange
    user_data = {
        "username": "testuser",
        "email": "test@example.com", 
        "hashed_password": hash_password("testpass123")
    }
    
    # Act
    user = User(**user_data)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    # Assert
    assert user.id is not None
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.hashed_password != "testpass123"  # Should be hashed
    assert user.is_active is True  # Default value


def test_user_password_verification(db_session):
    """Test password hashing and verification"""
    # Arrange
    plain_password = "mysecretpassword"
    user = User(
        username="passworduser",
        email="pwd@example.com",
        hashed_password=hash_password(plain_password)
    )
    db_session.add(user)
    db_session.commit()
    
    # Act & Assert
    assert verify_password(plain_password, user.hashed_password) is True
    assert verify_password("wrongpassword", user.hashed_password) is False


def test_user_unique_constraints(db_session):
    """Test that username and email must be unique"""
    # Arrange - Create first user
    user1 = User(
        username="uniqueuser",
        email="unique@example.com",
        hashed_password=hash_password("password123")
    )
    db_session.add(user1)
    db_session.commit()
    
    # Act & Assert - Try to create user with same username
    with pytest.raises(Exception):  # Should raise IntegrityError
        user2 = User(
            username="uniqueuser",  # Same username
            email="different@example.com",
            hashed_password=hash_password("password456")
        )
        db_session.add(user2)
        db_session.commit()
    
    # Reset session after error
    db_session.rollback()
    
    # Act & Assert - Try to create user with same email  
    with pytest.raises(Exception):  # Should raise IntegrityError
        user3 = User(
            username="differentuser",
            email="unique@example.com",  # Same email
            hashed_password=hash_password("password789")
        )
        db_session.add(user3)
        db_session.commit()


def test_user_polls_relationship(db_session):
    """Test that User has relationship with polls (empty initially)"""
    # Arrange
    user = User(
        username="pollowner",
        email="polls@example.com",
        hashed_password=hash_password("pollpass123")
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    # Act & Assert
    assert hasattr(user, 'polls')
    assert len(user.polls) == 0  # No polls initially


def test_user_query_by_username(db_session):
    """Test that we can query users by username"""
    # Arrange
    user = User(
        username="queryuser", 
        email="query@example.com",
        hashed_password=hash_password("querypass123")
    )
    db_session.add(user)
    db_session.commit()
    
    # Act
    found_user = db_session.query(User).filter(User.username == "queryuser").first()
    
    # Assert
    assert found_user is not None
    assert found_user.username == "queryuser"
    assert found_user.email == "query@example.com"


def test_user_query_by_email(db_session):
    """Test that we can query users by email"""
    # Arrange
    user = User(
        username="emailuser",
        email="email@example.com", 
        hashed_password=hash_password("emailpass123")
    )
    db_session.add(user)
    db_session.commit()
    
    # Act
    found_user = db_session.query(User).filter(User.email == "email@example.com").first()
    
    # Assert
    assert found_user is not None
    assert found_user.username == "emailuser"
    assert found_user.email == "email@example.com"


def test_user_soft_delete_functionality(db_session):
    """Test user deactivation (soft delete)"""
    # Arrange
    user = User(
        username="deleteuser",
        email="delete@example.com",
        hashed_password=hash_password("deletepass123")
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    # Assert initial state
    assert user.is_active is True
    
    # Act - Soft delete
    user.is_active = False
    db_session.commit()
    db_session.refresh(user)
    
    # Assert
    assert user.is_active is False
    # User still exists in database but is inactive
    found_user = db_session.query(User).filter(User.username == "deleteuser").first()
    assert found_user is not None
    assert found_user.is_active is False