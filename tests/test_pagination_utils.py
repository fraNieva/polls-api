"""
Tests for pagination utilities.

This module tests the reusable pagination logic to ensure it works correctly
across all API endpoints.
"""

import pytest
from sqlalchemy.orm import Session, declarative_base
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from typing import List

from app.api.v1.utils.pagination import (
    PaginationParams,
    PaginationMeta,
    get_pagination_params,
    calculate_pagination_metadata,
    apply_pagination,
    apply_search,
    create_paginated_response,
    paginate_query
)
from app.schemas.common import PaginatedResponse


# Test model for pagination testing
Base = declarative_base()

class TestModel(Base):
    __tablename__ = "test_items"
    
    id = Column(Integer, primary_key=True)
    title = Column(String(100))
    description = Column(String(500))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Add this to avoid pytest collection warning
    def __init__(self, **kwargs):
        # Call parent constructor with only valid column arguments
        valid_args = {k: v for k, v in kwargs.items() if hasattr(self.__class__, k)}
        super().__init__(**valid_args)


@pytest.fixture
def in_memory_db():
    """Create an in-memory SQLite database for testing"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    session = SessionLocal()
    
    # Create test data
    test_items = [
        TestModel(title=f"Item {i}", description=f"Description {i}", is_active=i % 2 == 0)
        for i in range(1, 26)  # Create 25 test items
    ]
    session.add_all(test_items)
    session.commit()
    
    yield session
    session.close()


class TestPaginationParams:
    """Test PaginationParams class"""
    
    def test_pagination_params_creation(self):
        """Test creating PaginationParams"""
        params = PaginationParams(page=2, size=10)
        assert params.page == 2
        assert params.size == 10
    
    def test_offset_calculation(self):
        """Test offset calculation"""
        params = PaginationParams(page=1, size=10)
        assert params.offset == 0
        
        params = PaginationParams(page=2, size=10)
        assert params.offset == 10
        
        params = PaginationParams(page=3, size=5)
        assert params.offset == 10


class TestPaginationMeta:
    """Test pagination metadata calculations"""
    
    def test_calculate_pagination_metadata(self):
        """Test pagination metadata calculation"""
        pagination = PaginationParams(page=1, size=10)
        metadata = calculate_pagination_metadata(total=25, pagination=pagination)
        
        assert metadata.total == 25
        assert metadata.page == 1
        assert metadata.size == 10
        assert metadata.pages == 3  # ceil(25/10)
        assert metadata.has_next is True
        assert metadata.has_prev is False
    
    def test_pagination_metadata_last_page(self):
        """Test pagination metadata for last page"""
        pagination = PaginationParams(page=3, size=10)
        metadata = calculate_pagination_metadata(total=25, pagination=pagination)
        
        assert metadata.page == 3
        assert metadata.pages == 3
        assert metadata.has_next is False
        assert metadata.has_prev is True
    
    def test_pagination_metadata_empty_results(self):
        """Test pagination metadata with no results"""
        pagination = PaginationParams(page=1, size=10)
        metadata = calculate_pagination_metadata(total=0, pagination=pagination)
        
        assert metadata.total == 0
        assert metadata.pages == 1
        assert metadata.has_next is False
        assert metadata.has_prev is False


class TestQueryUtils:
    """Test query utility functions"""
    
    def test_apply_pagination(self, in_memory_db: Session):
        """Test applying pagination to a query"""
        query = in_memory_db.query(TestModel)
        pagination = PaginationParams(page=2, size=5)
        
        paginated_query = apply_pagination(query, pagination)
        results = paginated_query.all()
        
        assert len(results) == 5
        assert results[0].id == 6  # Should start from 6th item (offset 5)
    
    def test_apply_search_single_field(self, in_memory_db: Session):
        """Test search functionality on a single field"""
        query = in_memory_db.query(TestModel)
        
        # Search for items with "1" in title
        search_query = apply_search(query, "1", [TestModel.title])
        results = search_query.all()
        
        # Should find items with titles containing "1" (Item 1, Item 10-19, Item 21)
        expected_count = 12  # Item 1, Item 10, Item 11, ..., Item 19, Item 21
        assert len(results) == expected_count
    
    def test_apply_search_multiple_fields(self, in_memory_db: Session):
        """Test search functionality on multiple fields"""
        query = in_memory_db.query(TestModel)
        
        # Search for "1" in both title and description
        search_query = apply_search(query, "1", [TestModel.title, TestModel.description])
        results = search_query.all()
        
        # Should find more results since we're searching in both fields
        assert len(results) >= 12
    
    def test_apply_search_no_term(self, in_memory_db: Session):
        """Test search with no search term"""
        query = in_memory_db.query(TestModel)
        original_count = query.count()
        
        search_query = apply_search(query, None, [TestModel.title])
        assert search_query.count() == original_count
        
        search_query = apply_search(query, "", [TestModel.title])
        assert search_query.count() == original_count
    
    def test_apply_search_no_fields(self, in_memory_db: Session):
        """Test search with no search fields"""
        query = in_memory_db.query(TestModel)
        original_count = query.count()
        
        search_query = apply_search(query, "test", [])
        assert search_query.count() == original_count


class TestPaginatedResponse:
    """Test paginated response creation"""
    
    def test_create_paginated_response(self, in_memory_db: Session):
        """Test creating a paginated response"""
        # Get some test items
        items = in_memory_db.query(TestModel).limit(5).all()
        pagination = PaginationParams(page=1, size=5)
        
        response = create_paginated_response(items, total=25, pagination=pagination)
        
        assert len(response.items) == 5
        assert response.total == 25
        assert response.page == 1
        assert response.size == 5
        assert response.pages == 5  # ceil(25/5)
        assert response.has_next is True
        assert response.has_prev is False


class TestPaginateQuery:
    """Test complete pagination workflow"""
    
    def test_paginate_query_basic(self, in_memory_db: Session):
        """Test basic query pagination"""
        query = in_memory_db.query(TestModel)
        pagination = PaginationParams(page=1, size=10)
        
        items, total = paginate_query(query, pagination)
        
        assert len(items) == 10
        assert total == 25
        assert items[0].id == 1
    
    def test_paginate_query_with_search(self, in_memory_db: Session):
        """Test query pagination with search"""
        query = in_memory_db.query(TestModel)
        pagination = PaginationParams(page=1, size=5)
        
        items, total = paginate_query(
            query, 
            pagination, 
            search_term="1",
            search_fields=[TestModel.title]
        )
        
        assert len(items) <= 5
        assert total >= 10  # At least items 1, 10-19, 21
        # All returned items should have "1" in title
        for item in items:
            assert "1" in item.title
    
    def test_paginate_query_second_page(self, in_memory_db: Session):
        """Test pagination on second page"""
        query = in_memory_db.query(TestModel)
        pagination = PaginationParams(page=2, size=10)
        
        items, total = paginate_query(query, pagination)
        
        assert len(items) == 10
        assert total == 25
        assert items[0].id == 11  # Should start from 11th item
    
    def test_paginate_query_last_page(self, in_memory_db: Session):
        """Test pagination on last page with partial results"""
        query = in_memory_db.query(TestModel)
        pagination = PaginationParams(page=3, size=10)
        
        items, total = paginate_query(query, pagination)
        
        assert len(items) == 5  # Only 5 items left on last page
        assert total == 25
        assert items[0].id == 21  # Should start from 21st item


class TestPaginationIntegration:
    """Integration tests for pagination utilities"""
    
    def test_full_pagination_workflow(self, in_memory_db: Session):
        """Test complete pagination workflow"""
        # Simulate what happens in an endpoint
        query = in_memory_db.query(TestModel)
        pagination = PaginationParams(page=2, size=8)
        
        # Apply search
        search_query = apply_search(query, "1", [TestModel.title])
        
        # Get total count
        total = search_query.count()
        
        # Apply pagination
        paginated_query = apply_pagination(search_query, pagination)
        items = paginated_query.all()
        
        # Create response
        response = create_paginated_response(items, total, pagination)
        
        # Verify response structure
        assert isinstance(response, PaginatedResponse)
        assert response.page == 2
        assert response.size == 8
        assert response.total == total
        assert len(response.items) <= 8
    
    def test_edge_case_no_results(self, in_memory_db: Session):
        """Test pagination with no results"""
        query = in_memory_db.query(TestModel).filter(TestModel.title == "nonexistent")
        pagination = PaginationParams(page=1, size=10)
        
        items, total = paginate_query(query, pagination)
        response = create_paginated_response(items, total, pagination)
        
        assert len(items) == 0
        assert total == 0
        assert response.pages == 1
        assert response.has_next is False
        assert response.has_prev is False