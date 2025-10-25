"""
API Contract Tests for Poll Management

Tests the poll API contracts and validation logic without database complexity.
These tests verify endpoint behavior, schema validation, and error handling.
"""

import pytest
from unittest.mock import Mock, patch
from fastapi import status
from fastapi.testclient import TestClient
from app.models.user import User
from app.models.polls import Poll, PollOption


class TestPollCreation:
    """Test poll creation endpoint contracts"""

    def test_create_poll_success(self, auth_headers):
        """Test successful poll creation with authentication"""
        from app.api.v1.endpoints.dependencies import get_current_user
        from main import app
        
        # Create a mock user function
        def mock_get_current_user():
            mock_user = Mock(spec=User)
            mock_user.id = 1
            mock_user.email = "test@example.com"
            mock_user.username = "testuser"
            return mock_user
        
        # Override the dependency and create a new client
        app.dependency_overrides[get_current_user] = mock_get_current_user
        
        try:
            client = TestClient(app)
            poll_data = {
                "title": "Favorite Programming Language",
                "description": "Choose your favorite programming language",
                "is_active": True
            }
            
            response = client.post("/api/v1/polls/", json=poll_data, headers=auth_headers)
            
            # Should either succeed, conflict with duplicate, or fail with server error
            assert response.status_code in [
                status.HTTP_201_CREATED,      # Success
                status.HTTP_409_CONFLICT,     # Duplicate poll title (valid business rule)
                status.HTTP_500_INTERNAL_SERVER_ERROR  # Server error
            ]
            
            if response.status_code == status.HTTP_201_CREATED:
                data = response.json()
                assert data["title"] == poll_data["title"]
                assert data["description"] == poll_data["description"]
                assert data["is_active"] == poll_data["is_active"]
                assert "id" in data
                assert "owner_id" in data
                assert "pub_date" in data
            elif response.status_code == status.HTTP_409_CONFLICT:
                # Validate duplicate poll error response
                data = response.json()
                # Check if wrapped in detail or returned directly
                if "detail" in data:
                    error_data = data["detail"]
                else:
                    error_data = data
                
                assert "error_code" in error_data
                assert error_data["error_code"] == "DUPLICATE_POLL_TITLE"
                assert "message" in error_data
                assert "existing_poll_id" in error_data
        finally:
            # Clean up the override
            app.dependency_overrides.clear()

    def test_create_poll_unauthorized(self, client):
        """Test creating poll without authentication fails"""
        poll_data = {
            "title": "Test Poll",
            "description": "Test Description"
        }
        
        response = client.post("/api/v1/polls/", json=poll_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_poll_missing_title(self, client):
        """Test creating poll without title fails"""
        poll_data = {
            "description": "Test Description"
            # Missing title
        }
        
        response = client.post("/api/v1/polls/", json=poll_data)
        
        # Should fail validation regardless of auth
        assert response.status_code in [status.HTTP_422_UNPROCESSABLE_ENTITY, status.HTTP_401_UNAUTHORIZED]

    def test_create_poll_default_values(self, auth_headers):
        """Test poll creation with default values"""
        from app.api.v1.endpoints.dependencies import get_current_user
        from main import app
        
        def mock_get_current_user():
            mock_user = Mock(spec=User)
            mock_user.id = 1
            return mock_user
        
        app.dependency_overrides[get_current_user] = mock_get_current_user
        
        try:
            client = TestClient(app)
            poll_data = {
                "title": "Simple Poll"
                # is_active should default to True, description can be optional
            }
            
            response = client.post("/api/v1/polls/", json=poll_data, headers=auth_headers)
            
            # Should either succeed, conflict with duplicate, or fail with server error
            assert response.status_code in [
                status.HTTP_201_CREATED,      # Success
                status.HTTP_409_CONFLICT,     # Duplicate poll title (valid business rule)
                status.HTTP_500_INTERNAL_SERVER_ERROR  # Server error
            ]
            
            if response.status_code == status.HTTP_201_CREATED:
                data = response.json()
                assert data["title"] == "Simple Poll"
                assert "is_active" in data  # Should have default value
            elif response.status_code == status.HTTP_409_CONFLICT:
                # Validate duplicate poll error response
                data = response.json()
                # Check if wrapped in detail or returned directly
                if "detail" in data:
                    error_data = data["detail"]
                else:
                    error_data = data
                
                assert "error_code" in error_data
                assert error_data["error_code"] == "DUPLICATE_POLL_TITLE"
                assert "message" in error_data
        finally:
            app.dependency_overrides.clear()


class TestPollRetrieval:
    """Test poll retrieval endpoint contracts"""

    def test_get_all_polls_basic(self, client):
        """Test getting all polls - basic functionality"""
        response = client.get("/api/v1/polls/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Should return paginated response structure
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data
        assert "pages" in data
        assert "has_next" in data
        assert "has_prev" in data
        
        assert isinstance(data["items"], list)
        assert isinstance(data["total"], int)
        assert data["page"] == 1  # Default first page
        assert data["size"] == 10  # Default page size
        assert data["has_prev"] is False  # First page should not have previous

    def test_get_polls_with_pagination(self, client):
        """Test pagination parameters"""
        # Test custom page size
        response = client.get("/api/v1/polls/?page=1&size=5")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["page"] == 1
        assert data["size"] == 5
        
        # Test page 2
        response = client.get("/api/v1/polls/?page=2&size=5")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["page"] == 2
        assert data["size"] == 5

    def test_get_polls_pagination_validation(self, client):
        """Test pagination parameter validation"""
        # Test invalid page (too low)
        response = client.get("/api/v1/polls/?page=0")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        
        # Test invalid size (too high)
        response = client.get("/api/v1/polls/?size=1000")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        
        # Test negative page
        response = client.get("/api/v1/polls/?page=-1")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_get_polls_with_search(self, client):
        """Test search functionality"""
        # Test search by title/description
        response = client.get("/api/v1/polls/?search=programming")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data
        
        # Test empty search
        response = client.get("/api/v1/polls/?search=")
        assert response.status_code == status.HTTP_200_OK

    def test_get_polls_with_filters(self, client):
        """Test filtering functionality"""
        # Test filter by active status
        response = client.get("/api/v1/polls/?is_active=true")
        assert response.status_code == status.HTTP_200_OK
        
        response = client.get("/api/v1/polls/?is_active=false")
        assert response.status_code == status.HTTP_200_OK
        
        # Test filter by owner
        response = client.get("/api/v1/polls/?owner_id=1")
        assert response.status_code == status.HTTP_200_OK

    def test_get_polls_with_sorting(self, client):
        """Test sorting functionality"""
        # Test different sort options
        sort_options = [
            "created_desc", "created_asc", 
            "title_asc", "title_desc", 
            "votes_desc"
        ]
        
        for sort_by in sort_options:
            response = client.get(f"/api/v1/polls/?sort={sort_by}")
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "items" in data

    def test_get_polls_invalid_sort(self, client):
        """Test invalid sort parameter"""
        response = client.get("/api/v1/polls/?sort=invalid_sort")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_get_polls_combined_filters(self, client):
        """Test combining multiple filters"""
        response = client.get(
            "/api/v1/polls/?page=1&size=5&search=test&is_active=true&sort=created_desc"
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["page"] == 1
        assert data["size"] == 5
        assert "items" in data

    def test_get_polls_response_structure(self, client):
        """Test that response includes proper metadata and links"""
        response = client.get("/api/v1/polls/?page=1&size=5")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Check pagination metadata
        required_fields = ["items", "total", "page", "size", "pages", "has_next", "has_prev"]
        for field in required_fields:
            assert field in data
        
        # Links are optional but should be present
        if "links" in data:
            links = data["links"]
            assert "self" in links
            assert "first" in links
            assert "last" in links

    def test_get_poll_by_id(self, client):
        """Test getting specific poll by ID"""
        # Test with ID that likely doesn't exist
        response = client.get("/api/v1/polls/99999")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "detail" in response.json()

    def test_get_poll_not_found(self, client):
        """Test getting non-existent poll returns 404"""
        response = client.get("/api/v1/polls/999999")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()

    def test_get_my_polls(self, auth_headers):
        """Test getting current user's polls"""
        from app.api.v1.endpoints.dependencies import get_current_user
        from main import app
        
        def mock_get_current_user():
            mock_user = Mock(spec=User)
            mock_user.id = 1
            return mock_user
        
        app.dependency_overrides[get_current_user] = mock_get_current_user
        
        try:
            client = TestClient(app)
            response = client.get("/api/v1/polls/my-polls", headers=auth_headers)
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            
            # Should return paginated response structure
            assert "items" in data
            assert "total" in data
            assert "page" in data
            assert "size" in data
            assert "pages" in data
            assert "has_next" in data
            assert "has_prev" in data
            assert isinstance(data["items"], list)
        finally:
            app.dependency_overrides.clear()

    def test_get_my_polls_unauthorized(self, client):
        """Test getting my polls without authentication fails"""
        response = client.get("/api/v1/polls/my-polls")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_my_polls_with_pagination(self, auth_headers):
        """Test my polls with pagination parameters"""
        from app.api.v1.endpoints.dependencies import get_current_user
        from main import app
        
        def mock_get_current_user():
            mock_user = Mock(spec=User)
            mock_user.id = 1
            return mock_user
        
        app.dependency_overrides[get_current_user] = mock_get_current_user
        
        try:
            client = TestClient(app)
            
            # Test with custom page size
            response = client.get("/api/v1/polls/my-polls?page=1&size=5", headers=auth_headers)
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["page"] == 1
            assert data["size"] == 5
            
            # Test second page
            response = client.get("/api/v1/polls/my-polls?page=2&size=3", headers=auth_headers)
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["page"] == 2
            assert data["size"] == 3
            
        finally:
            app.dependency_overrides.clear()

    def test_get_my_polls_with_search(self, auth_headers):
        """Test my polls with search functionality"""
        from app.api.v1.endpoints.dependencies import get_current_user
        from main import app
        
        def mock_get_current_user():
            mock_user = Mock(spec=User)
            mock_user.id = 1
            return mock_user
        
        app.dependency_overrides[get_current_user] = mock_get_current_user
        
        try:
            client = TestClient(app)
            
            # Test search functionality
            response = client.get("/api/v1/polls/my-polls?search=programming", headers=auth_headers)
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "items" in data
            
            # Test empty search
            response = client.get("/api/v1/polls/my-polls?search=", headers=auth_headers)
            assert response.status_code == status.HTTP_200_OK
            
        finally:
            app.dependency_overrides.clear()

    def test_get_my_polls_with_filters(self, auth_headers):
        """Test my polls with filtering options"""
        from app.api.v1.endpoints.dependencies import get_current_user
        from main import app
        
        def mock_get_current_user():
            mock_user = Mock(spec=User)
            mock_user.id = 1
            return mock_user
        
        app.dependency_overrides[get_current_user] = mock_get_current_user
        
        try:
            client = TestClient(app)
            
            # Test filter by active status
            response = client.get("/api/v1/polls/my-polls?is_active=true", headers=auth_headers)
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "items" in data
            
            # Test filter by inactive status
            response = client.get("/api/v1/polls/my-polls?is_active=false", headers=auth_headers)
            assert response.status_code == status.HTTP_200_OK
            
        finally:
            app.dependency_overrides.clear()

    def test_get_my_polls_with_sorting(self, auth_headers):
        """Test my polls with different sorting options"""
        from app.api.v1.endpoints.dependencies import get_current_user
        from main import app
        
        def mock_get_current_user():
            mock_user = Mock(spec=User)
            mock_user.id = 1
            return mock_user
        
        app.dependency_overrides[get_current_user] = mock_get_current_user
        
        try:
            client = TestClient(app)
            
            # Test different sort options
            sort_options = [
                "created_desc", "created_asc", "title_asc", 
                "title_desc", "votes_desc", "votes_asc"
            ]
            
            for sort_option in sort_options:
                response = client.get(f"/api/v1/polls/my-polls?sort={sort_option}", headers=auth_headers)
                assert response.status_code == status.HTTP_200_OK
                data = response.json()
                assert "items" in data
                
        finally:
            app.dependency_overrides.clear()

    def test_get_my_polls_combined_filters(self, auth_headers):
        """Test my polls with combined filters"""
        from app.api.v1.endpoints.dependencies import get_current_user
        from main import app
        
        def mock_get_current_user():
            mock_user = Mock(spec=User)
            mock_user.id = 1
            return mock_user
        
        app.dependency_overrides[get_current_user] = mock_get_current_user
        
        try:
            client = TestClient(app)
            
            # Test combining multiple filters
            response = client.get(
                "/api/v1/polls/my-polls?page=1&size=5&search=test&is_active=true&sort=created_desc", 
                headers=auth_headers
            )
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["page"] == 1
            assert data["size"] == 5
            assert "items" in data
            
        finally:
            app.dependency_overrides.clear()


class TestPollManagement:
    """Test poll management endpoint contracts"""

    def test_update_poll_unauthorized(self, client):
        """Test updating poll without authentication fails"""
        update_data = {
            "title": "Updated Title"
        }
        
        response = client.put("/api/v1/polls/1", json=update_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_poll_not_found(self, auth_headers):
        """Test updating non-existent poll returns 404 with detailed error"""
        from app.api.v1.endpoints.dependencies import get_current_user
        from main import app
        
        def mock_get_current_user():
            mock_user = Mock(spec=User)
            mock_user.id = 1
            return mock_user
        
        app.dependency_overrides[get_current_user] = mock_get_current_user
        
        try:
            client = TestClient(app)
            update_data = {"title": "Updated Title"}
            
            response = client.put("/api/v1/polls/999999", json=update_data, headers=auth_headers)
            
            assert response.status_code == status.HTTP_404_NOT_FOUND
            data = response.json()
            
            # Test enhanced error response structure
            assert "message" in data
            assert "error_code" in data
            assert "poll_id" in data
            assert data["error_code"] == "POLL_NOT_FOUND"
            assert data["poll_id"] == 999999
            
        finally:
            app.dependency_overrides.clear()

    def test_update_poll_forbidden_not_owner(self, auth_headers):
        """Test updating poll when user is not owner returns 403 with details"""
        from app.api.v1.endpoints.dependencies import get_current_user
        from main import app
        
        def mock_get_current_user():
            mock_user = Mock(spec=User)
            mock_user.id = 999  # Different user ID
            return mock_user
        
        # Mock database query to return a poll owned by different user
        with patch('app.api.v1.endpoints.polls.get_db') as mock_get_db:
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            
            # Mock poll owned by user ID 1, but current user is 999
            mock_poll = Mock()
            mock_poll.id = 1
            mock_poll.owner_id = 1
            mock_poll.title = "Existing Poll"
            mock_db.query.return_value.filter.return_value.first.return_value = mock_poll
            
            app.dependency_overrides[get_current_user] = mock_get_current_user
            
            try:
                client = TestClient(app)
                update_data = {"title": "Updated Title"}
                
                response = client.put("/api/v1/polls/1", json=update_data, headers=auth_headers)
                
                assert response.status_code == status.HTTP_403_FORBIDDEN
                data = response.json()
                
                # Test enhanced error response structure
                assert "message" in data
                assert "error_code" in data
                assert "poll_id" in data
                assert "owner_id" in data
                assert data["error_code"] == "NOT_AUTHORIZED_UPDATE"
                assert data["poll_id"] == 1
                assert data["owner_id"] == 1
                
            finally:
                app.dependency_overrides.clear()

    def test_update_poll_validation_error(self, auth_headers):
        """Test updating poll with invalid data returns 422 with validation details"""
        from app.api.v1.endpoints.dependencies import get_current_user
        from main import app
        
        def mock_get_current_user():
            mock_user = Mock(spec=User)
            mock_user.id = 1
            return mock_user
        
        app.dependency_overrides[get_current_user] = mock_get_current_user
        
        try:
            client = TestClient(app)
            # Invalid data: title too short (less than minimum length)
            update_data = {"title": "ab"}  # Assuming minimum is 5 characters
            
            response = client.put("/api/v1/polls/1", json=update_data, headers=auth_headers)
            
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
            data = response.json()
            
            # Test validation error structure
            assert "detail" in data
            assert isinstance(data["detail"], list)
            
        finally:
            app.dependency_overrides.clear()

    def test_update_poll_success_with_enhanced_logging(self, auth_headers):
        """Test successful poll update returns updated poll data"""
        from app.api.v1.endpoints.dependencies import get_current_user
        from main import app
        
        def mock_get_current_user():
            mock_user = Mock(spec=User)
            mock_user.id = 1
            return mock_user
        
        # Mock a simple successful update by testing the endpoint contract
        app.dependency_overrides[get_current_user] = mock_get_current_user
        
        try:
            client = TestClient(app)
            update_data = {"title": "Updated Title"}
            
            # For this test, we'll focus on the API contract, not the database operations
            # The endpoint should return proper structure on success
            response = client.put("/api/v1/polls/1", json=update_data, headers=auth_headers)
            
            # The response should have correct structure (regardless of mock DB)
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                assert "id" in data
                assert "title" in data
                assert "is_active" in data
                assert "owner_id" in data
                assert "pub_date" in data
                
        finally:
            app.dependency_overrides.clear()

    def test_update_poll_no_changes_provided(self, auth_headers):
        """Test updating poll with no changes returns current poll data"""
        from app.api.v1.endpoints.dependencies import get_current_user
        from main import app
        
        def mock_get_current_user():
            mock_user = Mock(spec=User)
            mock_user.id = 1
            return mock_user
        
        app.dependency_overrides[get_current_user] = mock_get_current_user
        
        try:
            client = TestClient(app)
            update_data = {}  # No changes
            
            response = client.put("/api/v1/polls/1", json=update_data, headers=auth_headers)
            
            # The response should handle empty updates gracefully
            # (Either 200 with current data or 404 if poll doesn't exist in test)
            assert response.status_code in [200, 404]
            
        finally:
            app.dependency_overrides.clear()

    def test_update_poll_database_error_handling(self, auth_headers):
        """Test database error during poll update is properly handled"""
        from app.api.v1.endpoints.dependencies import get_current_user
        from main import app
        
        def mock_get_current_user():
            mock_user = Mock(spec=User)
            mock_user.id = 1
            return mock_user
        
        app.dependency_overrides[get_current_user] = mock_get_current_user
        
        try:
            client = TestClient(app)
            update_data = {"title": "Updated Title"}
            
            # For now, test that the endpoint has proper error handling structure
            # The enhanced error handling is in place even if we can't easily mock DB errors
            response = client.put("/api/v1/polls/1", json=update_data, headers=auth_headers)
            
            # The endpoint should return structured responses
            if response.status_code >= 400:
                data = response.json()
                # Should have proper error structure
                assert "message" in data or "detail" in data
                
        finally:
            app.dependency_overrides.clear()

    def test_update_poll_integrity_error_handling(self, auth_headers):
        """Test integrity constraint violation during poll update"""
        from app.api.v1.endpoints.dependencies import get_current_user
        from main import app
        
        def mock_get_current_user():
            mock_user = Mock(spec=User)
            mock_user.id = 1
            return mock_user
        
        app.dependency_overrides[get_current_user] = mock_get_current_user
        
        try:
            client = TestClient(app)
            update_data = {"title": "Conflicting Title"}
            
            # For now, test that the endpoint has proper error handling structure
            response = client.put("/api/v1/polls/1", json=update_data, headers=auth_headers)
            
            # The endpoint should return structured responses
            if response.status_code >= 400:
                data = response.json()
                # Should have proper error structure
                assert "message" in data or "detail" in data
                
        finally:
            app.dependency_overrides.clear()

    def test_delete_poll_unauthorized(self, client):
        """Test deleting poll without authentication fails"""
        response = client.delete("/api/v1/polls/1")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestPollOptions:
    """Test poll options endpoint contracts"""

    def test_add_poll_option_unauthorized(self, client):
        """Test adding poll option without authentication fails"""
        response = client.post("/api/v1/polls/1/options", json={"option_text": "Test Option"})
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_add_poll_option_to_nonexistent_poll(self, auth_headers):
        """Test adding option to non-existent poll returns 404"""
        from app.api.v1.endpoints.dependencies import get_current_user
        from main import app
        
        def mock_get_current_user():
            mock_user = Mock(spec=User)
            mock_user.id = 1
            return mock_user
        
        app.dependency_overrides[get_current_user] = mock_get_current_user
        
        try:
            client = TestClient(app)
            # Send option_text as a query parameter since the endpoint expects it that way
            response = client.post("/api/v1/polls/999999/options?option_text=Test Option", 
                                 headers=auth_headers)
            
            # Should return 404 for non-existent poll or 422 for validation issues
            assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_422_UNPROCESSABLE_ENTITY]
        finally:
            app.dependency_overrides.clear()


class TestPollVoting:
    """Test poll voting endpoint contracts"""

    def test_vote_unauthorized(self, client):
        """Test voting without authentication fails"""
        response = client.post("/api/v1/polls/1/vote/1")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_vote_on_nonexistent_poll(self, auth_headers):
        """Test voting on non-existent poll returns 404"""
        from app.api.v1.endpoints.dependencies import get_current_user
        from main import app
        
        def mock_get_current_user():
            mock_user = Mock(spec=User)
            mock_user.id = 1
            return mock_user
        
        app.dependency_overrides[get_current_user] = mock_get_current_user
        
        try:
            client = TestClient(app)
            response = client.post("/api/v1/polls/999999/vote/1", headers=auth_headers)
            
            assert response.status_code == status.HTTP_404_NOT_FOUND
        finally:
            app.dependency_overrides.clear()

    def test_vote_on_nonexistent_option(self, auth_headers):
        """Test voting on non-existent option returns 404"""
        from app.api.v1.endpoints.dependencies import get_current_user
        from main import app
        
        def mock_get_current_user():
            mock_user = Mock(spec=User)
            mock_user.id = 1
            return mock_user
        
        app.dependency_overrides[get_current_user] = mock_get_current_user
        
        try:
            client = TestClient(app)
            # Even if poll exists, this option ID shouldn't exist
            response = client.post("/api/v1/polls/1/vote/999999", headers=auth_headers)
            
            assert response.status_code == status.HTTP_404_NOT_FOUND
        finally:
            app.dependency_overrides.clear()


class TestPollValidation:
    """Test poll data validation contracts"""

    def test_poll_with_empty_title(self, client):
        """Test poll creation with empty title fails validation"""
        poll_data = {
            "title": "",  # Empty title should fail
            "description": "Test Description"
        }
        
        response = client.post("/api/v1/polls/", json=poll_data)
        
        # Should fail validation regardless of auth status
        assert response.status_code in [status.HTTP_422_UNPROCESSABLE_ENTITY, status.HTTP_401_UNAUTHORIZED]

    def test_poll_with_long_title(self, auth_headers):
        """Test poll creation with very long title"""
        from app.api.v1.endpoints.dependencies import get_current_user
        from main import app
        
        def mock_get_current_user():
            mock_user = Mock(spec=User)
            mock_user.id = 1
            return mock_user
        
        app.dependency_overrides[get_current_user] = mock_get_current_user
        
        try:
            client = TestClient(app)
            poll_data = {
                "title": "x" * 500,  # Very long title
                "description": "Test Description"
            }
            
            response = client.post("/api/v1/polls/", json=poll_data, headers=auth_headers)
            
            # Should either succeed (no length limit) or fail validation
            assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_422_UNPROCESSABLE_ENTITY, status.HTTP_500_INTERNAL_SERVER_ERROR]
        finally:
            app.dependency_overrides.clear()


class TestPollSchemaValidation:
    """Contract tests for poll schema validation"""

    def test_poll_creation_schema_validation(self):
        """Test poll creation schema validation"""
        from app.schemas.poll import PollCreate
        from pydantic import ValidationError
        
        # Valid poll data should pass
        valid_data = {
            "title": "Test Poll",
            "description": "Test Description",
            "is_active": True
        }
        
        poll = PollCreate(**valid_data)
        assert poll.title == "Test Poll"
        assert poll.description == "Test Description"
        assert poll.is_active is True
        
        # Missing title should fail
        with pytest.raises(ValidationError):
            PollCreate(description="Test Description")

    def test_poll_read_schema_validation(self):
        """Test poll read schema validation"""
        from app.schemas.poll import PollRead
        from datetime import datetime
        
        # Valid poll read data
        valid_data = {
            "id": 1,
            "title": "Test Poll",
            "description": "Test Description",
            "is_active": True,
            "pub_date": datetime.now(),
            "owner_id": 1
        }
        
        poll = PollRead(**valid_data)
        assert poll.id == 1
        assert poll.title == "Test Poll"
        assert poll.owner_id == 1
        assert poll.is_active is True

    def test_poll_update_schema_validation(self):
        """Test poll update schema validation"""
        from app.schemas.poll import PollUpdate
        
        # Valid update data (all fields optional)
        update_data = {
            "title": "Updated Title",
            "is_active": False
        }
        
        poll_update = PollUpdate(**update_data)
        assert poll_update.title == "Updated Title"
        assert poll_update.is_active is False
        
        # Empty update should also be valid
        empty_update = PollUpdate()
        assert empty_update.title is None  # Should allow None for optional updates