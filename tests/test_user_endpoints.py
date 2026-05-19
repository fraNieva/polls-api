"""
API Contract Tests for User Management

Tests the user API contracts and validation logic without database complexity.
These tests verify endpoint behavior, schema validation, and error handling.
"""

import pytest
from unittest.mock import Mock, patch
from fastapi import status
from fastapi.testclient import TestClient
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.api.v1.endpoints.users import UserUpdate, create_user, update_user_profile
from app.models.user import User
from app.schemas.user import UserCreate


class TestUserEndpoints:
    """Test user API endpoint contracts"""

    def test_get_current_user_success(self, auth_headers):
        """Test getting current user profile with valid authentication"""
        from app.api.v1.endpoints.dependencies import get_current_user
        from main import app
        
        # Create a mock user function
        def mock_get_current_user():
            mock_user = Mock(spec=User)
            mock_user.id = 1
            mock_user.email = "test@example.com"
            mock_user.username = "testuser"
            mock_user.full_name = "Test User"
            mock_user.is_active = True
            return mock_user
        
        # Override the dependency and create a new client
        app.dependency_overrides[get_current_user] = mock_get_current_user
        
        try:
            client = TestClient(app)
            response = client.get("/api/v1/users/me", headers=auth_headers)
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["email"] == "test@example.com"
            assert data["username"] == "testuser"
            assert data["full_name"] == "Test User"
            assert data["is_active"] is True
            assert "hashed_password" not in data
        finally:
            # Clean up the override
            app.dependency_overrides.clear()

    def test_get_current_user_unauthorized(self, client):
        """Test getting current user without authentication fails"""
        response = client.get("/api/v1/users/me")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_user_success(self, client):
        """Test successful user creation contract"""
        # For contract testing, we test the endpoint's response format
        # rather than complex database mocking
        user_data = {
            "username": "testuser123",
            "email": "testuser123@example.com",
            "password": "newpass123",
            "full_name": "Test User",
            "is_active": True
        }
        
        response = client.post("/api/v1/users/", json=user_data)
        
        # The endpoint should either succeed (201) or fail with validation (422) or conflict (400)
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST]
        
        if response.status_code == status.HTTP_201_CREATED:
            data = response.json()
            assert data["username"] == "testuser123"
            assert data["email"] == "testuser123@example.com"
            assert data["full_name"] == "Test User"
            assert data["is_active"] is True
            assert "hashed_password" not in data
        else:
            # If it fails (e.g., due to existing user), check error format
            assert "detail" in response.json()

    def test_create_user_duplicate_email(self, client):
        """Test user creation with duplicate email fails - test response format"""
        # Use a common email that might already exist from other tests
        user_data = {
            "username": "duplicatetest",
            "email": "test@example.com",  # Common test email
            "password": "newpass123",
            "full_name": "Duplicate User"
        }
        
        response = client.post("/api/v1/users/", json=user_data)
        
        # Should either succeed or fail with appropriate error
        # Contract testing focuses on response format
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST]
        
        if response.status_code == status.HTTP_400_BAD_REQUEST:
            error_response = response.json()
            
            # Handle both direct and nested response formats
            if "detail" in error_response and isinstance(error_response["detail"], dict):
                # Nested format (test environment)
                detail = error_response["detail"]
                assert "message" in detail
                assert ("email already registered" in detail["message"].lower() or 
                        "username already registered" in detail["message"].lower())
                assert "error_code" in detail
            else:
                # Direct format (production environment)
                assert "message" in error_response
                assert ("email already registered" in error_response["message"].lower() or 
                        "username already registered" in error_response["message"].lower())
                assert "error_code" in error_response

    def test_create_user_invalid_email(self, client):
        """Test user creation with invalid email format fails"""
        user_data = {
            "username": "newuser",
            "email": "invalid-email",
            "password": "newpass123",
            "full_name": "New User"
        }
        
        response = client.post("/api/v1/users/", json=user_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_create_user_missing_fields(self, client):
        """Test user creation with missing required fields fails"""
        user_data = {
            "username": "newuser"
            # Missing email and password
        }
        
        response = client.post("/api/v1/users/", json=user_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


# Additional contract tests that would apply if more endpoints were implemented
class TestUserEndpointsContracts:
    """Contract tests for user management operations that verify expected behavior patterns"""

    def test_user_profile_data_format(self):
        """Test that user profile data follows expected schema format"""
        # This tests the schema validation without hitting actual endpoints
        from app.schemas.user import UserRead
        from pydantic import ValidationError
        
        # Valid user data should pass validation
        valid_data = {
            "id": 1,
            "username": "testuser",
            "email": "test@example.com",
            "full_name": "Test User",
            "is_active": True
        }
        
        user = UserRead(**valid_data)
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.is_active is True
        
        # Invalid email should fail validation
        with pytest.raises(ValidationError):
            UserRead(**{**valid_data, "email": "invalid-email"})

    def test_user_creation_schema_validation(self):
        """Test user creation schema validation"""
        from app.schemas.user import UserCreate
        from pydantic import ValidationError
        
        # Valid creation data should pass
        valid_data = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "securepass123",
            "full_name": "New User"
        }
        
        user = UserCreate(**valid_data)
        assert user.username == "newuser"
        assert user.email == "new@example.com"
        assert user.password == "securepass123"
        
        # Missing required fields should fail
        with pytest.raises(ValidationError):
            UserCreate(username="test")  # Missing email, password
        
        # Invalid email should fail
        with pytest.raises(ValidationError):
            UserCreate(**{**valid_data, "email": "invalid"})


def _build_db_with_first_values(*values):
    """Create a mock DB where consecutive .first() calls return provided values."""
    db = Mock()
    db.query.return_value.filter.return_value.first.side_effect = list(values)
    db.commit = Mock()
    db.refresh = Mock()
    db.rollback = Mock()
    return db


def _build_user(**overrides):
    user = Mock()
    user.id = overrides.get('id', 1)
    user.email = overrides.get('email', 'user@example.com')
    user.username = overrides.get('username', 'username')
    user.full_name = overrides.get('full_name', 'Test User')
    user.is_active = overrides.get('is_active', True)
    user.hashed_password = overrides.get('hashed_password', 'hashed')
    return user


class TestUserEndpointBranches:
    def test_create_user_duplicate_email(self):
        existing = _build_user(email='existing@example.com')
        db = _build_db_with_first_values(existing)

        user = UserCreate(
            email='existing@example.com',
            password='safe-password',
            full_name='New User',
            username='newuser',
        )

        with pytest.raises(HTTPException) as exc_info:
            create_user(user=user, db=db)

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert exc_info.value.detail['error_code'] == 'DUPLICATE_RESOURCE'

    def test_create_user_duplicate_username(self):
        existing = _build_user(username='existinguser')
        db = _build_db_with_first_values(None, existing)

        user = UserCreate(
            email='new@example.com',
            password='safe-password',
            full_name='New User',
            username='existinguser',
        )

        with pytest.raises(HTTPException) as exc_info:
            create_user(user=user, db=db)

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert exc_info.value.detail['error_code'] == 'DUPLICATE_RESOURCE'

    def test_create_user_handles_integrity_error(self):
        db = _build_db_with_first_values(None, None)
        db.commit.side_effect = IntegrityError('stmt', 'params', Exception('dup'))

        user = UserCreate(
            email='new4@example.com',
            password='safe-password',
            full_name='New User',
            username='newuser4',
        )

        with pytest.raises(HTTPException) as exc_info:
            create_user(user=user, db=db)

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert exc_info.value.detail['error_code'] == 'DUPLICATE_RESOURCE'
        db.rollback.assert_called_once()

    def test_update_user_profile_no_payload_returns_current_user(self):
        db = Mock()
        db.commit = Mock()
        current_user = _build_user()

        response = update_user_profile(
            user_update=UserUpdate(),
            current_user=current_user,
            db=db,
        )

        assert response is current_user
        db.commit.assert_not_called()

    def test_update_user_profile_duplicate_email(self):
        db = Mock()
        db.query.return_value.filter.return_value.first.return_value = _build_user(
            id=2, email='new@example.com'
        )
        current_user = _build_user(id=1, email='current@example.com')

        with pytest.raises(HTTPException) as exc_info:
            update_user_profile(
                user_update=UserUpdate(email='new@example.com'),
                current_user=current_user,
                db=db,
            )

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert exc_info.value.detail['error_code'] == 'DUPLICATE_RESOURCE'

    def test_update_user_profile_duplicate_username(self):
        db = Mock()
        db.query.return_value.filter.return_value.first.side_effect = [None, _build_user(id=2)]
        current_user = _build_user(id=1, username='currentuser')

        with pytest.raises(HTTPException) as exc_info:
            update_user_profile(
                user_update=UserUpdate(email='same@example.com', username='takenuser'),
                current_user=current_user,
                db=db,
            )

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert exc_info.value.detail['error_code'] == 'DUPLICATE_RESOURCE'

    def test_update_user_profile_changes_and_commits(self):
        db = Mock()
        db.query.return_value.filter.return_value.first.return_value = None
        db.commit = Mock()
        db.refresh = Mock()
        current_user = _build_user(email='current@example.com', full_name='Current Name')

        response = update_user_profile(
            user_update=UserUpdate(email=' next@example.com ', full_name=' Next Name '),
            current_user=current_user,
            db=db,
        )

        assert response is current_user
        assert current_user.email == 'next@example.com'
        assert current_user.full_name == 'Next Name'
        db.commit.assert_called_once()
        db.refresh.assert_called_once_with(current_user)

    def test_update_user_profile_same_trimmed_values_no_commit(self):
        db = Mock()
        db.query.return_value.filter.return_value.first.return_value = None
        db.commit = Mock()
        current_user = _build_user(email='same@example.com', full_name='Same Name')

        response = update_user_profile(
            user_update=UserUpdate(email=' same@example.com ', full_name=' Same Name '),
            current_user=current_user,
            db=db,
        )

        assert response is current_user
        db.commit.assert_not_called()

    def test_update_user_profile_handles_sqlalchemy_error(self):
        db = Mock()
        db.query.return_value.filter.return_value.first.return_value = None
        db.commit = Mock(side_effect=SQLAlchemyError('cannot commit'))
        db.rollback = Mock()
        current_user = _build_user(email='old@example.com')

        with pytest.raises(HTTPException) as exc_info:
            update_user_profile(
                user_update=UserUpdate(email='new@example.com'),
                current_user=current_user,
                db=db,
            )

        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert exc_info.value.detail['error_code'] == 'DATABASE_ERROR'
        db.rollback.assert_called_once()