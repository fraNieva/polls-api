"""
Test-Driven Development tests for Poll functionality.

This demonstrates the TDD Red-Green-Refactor cycle:
1. Write failing tests first (RED)
2. Write minimal code to pass tests (GREEN)
3. Refactor while keeping tests green (REFACTOR)
"""

import pytest
from sqlalchemy import text
from app.models.user import User
from app.models.polls import Poll, PollOption, Vote
from app.core.security import hash_password


def test_poll_model_creation(db_session):
    """Test that we can create a Poll model instance with owner"""
    # Arrange - First create a user (owner)
    user = User(
        username="pollcreator",
        email="creator@example.com",
        hashed_password=hash_password("creatorpass123")
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    # Act - Create a poll
    poll = Poll(
        title="What's your favorite color?",
        description="A simple color preference poll",
        owner_id=user.id
    )
    db_session.add(poll)
    db_session.commit()
    db_session.refresh(poll)
    
    # Assert
    assert poll.id is not None
    assert poll.title == "What's your favorite color?"
    assert poll.description == "A simple color preference poll"
    assert poll.owner_id == user.id
    assert poll.owner.username == "pollcreator"
    assert poll.is_active is True  # Default value
    assert len(user.polls) == 1  # User has this poll


def test_poll_option_creation(db_session):
    """Test that we can create poll options for a poll"""
    # Arrange - Create user and poll
    user = User(
        username="optionuser",
        email="options@example.com",
        hashed_password=hash_password("optionpass123")
    )
    db_session.add(user)
    db_session.commit()
    
    poll = Poll(
        title="Best Framework",
        description="Choose the best web framework",
        owner_id=user.id
    )
    db_session.add(poll)
    db_session.commit()
    db_session.refresh(poll)
    
    # Act - Create poll options
    option1 = PollOption(text="FastAPI", poll_id=poll.id)
    option2 = PollOption(text="Django", poll_id=poll.id)
    option3 = PollOption(text="Flask", poll_id=poll.id)
    
    db_session.add_all([option1, option2, option3])
    db_session.commit()
    
    # Assert
    assert len(poll.options) == 3
    assert option1.text == "FastAPI"
    assert option1.vote_count == 0  # Default value
    assert all(opt.poll_id == poll.id for opt in poll.options)


def test_poll_voting_functionality(db_session):
    """Test that users can vote on poll options"""
    # Arrange - Create user, poll, and options
    owner = User(
        username="pollowner",
        email="owner@example.com",
        hashed_password=hash_password("ownerpass123")
    )
    voter = User(
        username="voter1",
        email="voter@example.com",
        hashed_password=hash_password("voterpass123")
    )
    db_session.add_all([owner, voter])
    db_session.commit()
    
    poll = Poll(
        title="Favorite Language",
        description="Programming language preference",
        owner_id=owner.id
    )
    db_session.add(poll)
    db_session.commit()
    
    option = PollOption(text="Python", poll_id=poll.id)
    db_session.add(option)
    db_session.commit()
    db_session.refresh(option)
    
    # Act - User votes
    vote = Vote(
        user_id=voter.id,
        poll_option_id=option.id,
        poll_id=poll.id  # Add poll_id
    )
    db_session.add(vote)
    db_session.commit()
    
    # Assert
    assert vote.user_id == voter.id
    assert vote.poll_option_id == option.id
    assert len(voter.votes) == 1
    # Note: vote_count update would need a trigger or method
    

def test_poll_cascade_delete(db_session):
    """Test that deleting a user cascades to their polls"""
    # Arrange - Create user with polls
    user = User(
        username="cascadeuser",
        email="cascade@example.com",
        hashed_password=hash_password("cascadepass123")
    )
    db_session.add(user)
    db_session.commit()
    
    poll1 = Poll(title="Poll 1", owner_id=user.id)
    poll2 = Poll(title="Poll 2", owner_id=user.id)
    db_session.add_all([poll1, poll2])
    db_session.commit()
    
    poll_ids = [poll1.id, poll2.id]
    
    # Act - Delete user
    db_session.delete(user)
    db_session.commit()
    
    # Assert - Polls should be deleted due to cascade
    remaining_polls = db_session.query(Poll).filter(Poll.id.in_(poll_ids)).all()
    assert len(remaining_polls) == 0


def test_poll_active_status(db_session):
    """Test poll activation/deactivation functionality"""
    # Arrange
    user = User(
        username="statususer",
        email="status@example.com",
        hashed_password=hash_password("statuspass123")
    )
    db_session.add(user)
    db_session.commit()
    
    poll = Poll(
        title="Status Test Poll",
        description="Testing poll status changes",
        owner_id=user.id
    )
    db_session.add(poll)
    db_session.commit()
    db_session.refresh(poll)
    
    # Assert initial state
    assert poll.is_active is True
    
    # Act - Deactivate poll
    poll.is_active = False
    db_session.commit()
    db_session.refresh(poll)
    
    # Assert
    assert poll.is_active is False


def test_user_cannot_vote_twice_on_same_poll(db_session):
    """Test that a user cannot vote twice on the same poll (business rule)"""
    # Arrange - Setup user, poll, and options
    owner = User(username="owner", email="own@test.com", hashed_password=hash_password("pass"))
    voter = User(username="voter", email="vote@test.com", hashed_password=hash_password("pass"))
    db_session.add_all([owner, voter])
    db_session.commit()
    
    poll = Poll(title="Single Vote Poll", owner_id=owner.id)
    db_session.add(poll)
    db_session.commit()
    
    option1 = PollOption(text="Option 1", poll_id=poll.id)
    option2 = PollOption(text="Option 2", poll_id=poll.id)
    db_session.add_all([option1, option2])
    db_session.commit()
    db_session.refresh(option1)
    db_session.refresh(option2)
    
    # Act - First vote
    vote1 = Vote(user_id=voter.id, poll_option_id=option1.id, poll_id=poll.id)
    db_session.add(vote1)
    db_session.commit()
    
    # Act & Assert - Second vote should fail (business logic constraint)
    # This test shows what we expect, implementation might need constraints
    with pytest.raises(Exception):  # Should raise integrity error
        vote2 = Vote(user_id=voter.id, poll_option_id=option2.id, poll_id=poll.id)  # Same user, same poll
        db_session.add(vote2)
        db_session.commit()


def test_poll_query_by_owner(db_session):
    """Test querying polls by owner"""
    # Arrange
    user1 = User(username="owner1", email="owner1@test.com", hashed_password=hash_password("pass"))
    user2 = User(username="owner2", email="owner2@test.com", hashed_password=hash_password("pass"))
    db_session.add_all([user1, user2])
    db_session.commit()
    
    poll1 = Poll(title="Poll by User 1", owner_id=user1.id)
    poll2 = Poll(title="Another Poll by User 1", owner_id=user1.id)
    poll3 = Poll(title="Poll by User 2", owner_id=user2.id)
    db_session.add_all([poll1, poll2, poll3])
    db_session.commit()
    
    # Act
    user1_polls = db_session.query(Poll).filter(Poll.owner_id == user1.id).all()
    
    # Assert
    assert len(user1_polls) == 2
    assert all(poll.owner_id == user1.id for poll in user1_polls)