import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

# Import basic dependencies
from app.db.database import Base, get_db

# Test database - in-memory SQLite  
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Test Fixtures
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.database import Base

# Import all models so SQLAlchemy can resolve relationships
from app.models.user import User
from app.models.polls import Poll, PollOption, Vote  # Import all models


@pytest.fixture(scope="function")
def db_session():
    """Create a test database session"""
    # Create in-memory SQLite database for testing
    test_engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    
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
def client(db_session):
    """Test client with fresh database"""
    # Import app here to avoid circular imports
    from main import app
    
    # Override the database dependency
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture
def sample_user_data():
    """Sample user data for testing"""
    return {
        "username": "testuser", 
        "email": "test@example.com",
        "full_name": "Test User",
        "password": "testpass123",
        "is_active": True
    }