import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# Import basic dependencies
from app.db.database import Base, get_db
from app.core.security import hash_password
from app.models.user import User
from app.models.polls import Poll, PollOption, Vote

# Test database - in-memory SQLite  
TEST_DB_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def db_session():
    """Create a test database session for direct database tests"""
    # Create in-memory SQLite database for testing
    test_engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    
    # Create all tables
    Base.metadata.create_all(bind=test_engine)
    
    # Create session
    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = testing_session_local()
    
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def mock_db_session():
    """Create a mock database session for API endpoint tests"""
    mock_session = MagicMock()
    mock_session.query.return_value = mock_session
    mock_session.filter.return_value = mock_session
    mock_session.first.return_value = None
    mock_session.all.return_value = []
    mock_session.add = MagicMock()
    mock_session.commit = MagicMock()
    mock_session.refresh = MagicMock()
    mock_session.delete = MagicMock()
    return mock_session


@pytest.fixture(scope="function")
def client():
    """Create a test client with mocked database for endpoint contract tests"""
    from fastapi import FastAPI
    from app.api.v1.endpoints import users, auth, polls
    
    # Create fresh app instance for testing
    app = FastAPI(title="Test Polls API", version="1.0.0")
    app.include_router(users.router, prefix="/api/v1")
    app.include_router(auth.router, prefix="/api/v1")
    app.include_router(polls.router, prefix="/api/v1")
    
    return TestClient(app)


# Database fixtures for TDD tests
@pytest.fixture
def test_user(db_session):
    """Create a test user in database (for database tests)"""
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=hash_password("testpass123")
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_user2(db_session):
    """Create a second test user in database (for database tests)"""
    user = User(
        username="testuser2",
        email="test2@example.com",
        hashed_password=hash_password("testpass123")
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_poll(db_session, test_user):
    """Create a test poll in database (for database tests)"""
    poll = Poll(
        title="Test Poll",
        description="A test poll for testing",
        owner_id=test_user.id
    )
    db_session.add(poll)
    db_session.commit()
    db_session.refresh(poll)
    return poll


@pytest.fixture
def test_poll_with_options(db_session, test_poll):
    """Create a test poll with options in database (for database tests)"""
    option1 = PollOption(text="Option 1", poll_id=test_poll.id)
    option2 = PollOption(text="Option 2", poll_id=test_poll.id)
    db_session.add_all([option1, option2])
    db_session.commit()
    db_session.refresh(option1)
    db_session.refresh(option2)
    test_poll.option1 = option1
    test_poll.option2 = option2
    return test_poll


# Mock fixtures for API endpoint tests
@pytest.fixture
def mock_user():
    """Mock user object for API tests"""
    user = Mock()
    user.id = 1
    user.username = "testuser"
    user.email = "test@example.com"
    user.full_name = "Test User"
    user.is_active = True
    user.hashed_password = hash_password("testpass123")
    return user


@pytest.fixture
def mock_user2():
    """Mock second user object for API tests"""
    user = Mock()
    user.id = 2
    user.username = "testuser2"
    user.email = "test2@example.com"
    user.full_name = "Test User 2"
    user.is_active = True
    user.hashed_password = hash_password("testpass123")
    return user


@pytest.fixture
def mock_poll():
    """Mock poll object for API tests"""
    poll = Mock()
    poll.id = 1
    poll.title = "Test Poll"
    poll.description = "A test poll for testing"
    poll.owner_id = 1
    poll.is_active = True
    return poll


@pytest.fixture
def auth_headers():
    """Mock authentication headers for API tests"""
    return {"Authorization": "Bearer mock_jwt_token"}


@pytest.fixture
def sample_user_data():
    """Sample user data for testing"""
    return {
        "username": "testuser", 
        "email": "test@example.com",
        "password": "testpass123"
    }