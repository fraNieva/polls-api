"""
Pagination utilities for API endpoints.

This module provides reusable pagination, filtering, and sorting utilities
to ensure consistency across all API endpoints.
"""

from typing import List, Optional, TypeVar, Any
from pydantic import BaseModel, Field
from fastapi import Query
from sqlalchemy.orm import Query as SQLQuery
import math

from app.core.constants import DatabaseConfig
from app.schemas.common import PaginatedResponse


# Generic type for paginated responses
T = TypeVar('T')


class PaginationParams(BaseModel):
    """Parameters for pagination"""
    page: int = Field(..., ge=1, description="Page number (starts from 1)")
    size: int = Field(..., ge=1, le=DatabaseConfig.MAX_PAGE_SIZE, description="Items per page")

    @property
    def offset(self) -> int:
        """Calculate offset for database query"""
        return (self.page - 1) * self.size


class PaginationMeta(BaseModel):
    """Pagination metadata for responses"""
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Items per page")
    pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there are more pages")
    has_prev: bool = Field(..., description="Whether there are previous pages")


def get_pagination_params(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(DatabaseConfig.DEFAULT_PAGE_SIZE, ge=1, le=DatabaseConfig.MAX_PAGE_SIZE, description="Items per page")
) -> PaginationParams:
    """FastAPI dependency for pagination parameters"""
    return PaginationParams(page=page, size=size)


def calculate_pagination_metadata(total: int, pagination: PaginationParams) -> PaginationMeta:
    """Calculate pagination metadata from total count and pagination parameters"""
    pages = math.ceil(total / pagination.size) if total > 0 else 1
    has_next = pagination.page < pages
    has_prev = pagination.page > 1
    
    return PaginationMeta(
        total=total,
        page=pagination.page,
        size=pagination.size,
        pages=pages,
        has_next=has_next,
        has_prev=has_prev
    )


def apply_pagination(query: SQLQuery, pagination: PaginationParams) -> SQLQuery:
    """Apply pagination to a SQLAlchemy query"""
    return query.offset(pagination.offset).limit(pagination.size)


def apply_search(
    query: SQLQuery, 
    search_term: Optional[str], 
    search_fields: List[Any]
) -> SQLQuery:
    """
    Apply case-insensitive search to specified fields.
    
    Args:
        query: SQLAlchemy query object
        search_term: Search string (optional)
        search_fields: List of model fields to search in
        
    Returns:
        Updated query with search filters applied
    """
    if not search_term or not search_fields:
        return query
        
    # Create OR conditions for all search fields
    search_conditions = []
    for field in search_fields:
        search_conditions.append(field.ilike(f"%{search_term}%"))
    
    # Apply OR condition to query
    if search_conditions:
        from sqlalchemy import or_
        query = query.filter(or_(*search_conditions))
    
    return query


def create_paginated_response(
    items: List[T],
    total: int,
    pagination: PaginationParams
) -> PaginatedResponse[T]:
    """
    Create a paginated response from items and pagination info.
    
    Args:
        items: List of items for current page
        total: Total number of items across all pages
        pagination: Pagination parameters
        
    Returns:
        PaginatedResponse with items and metadata
    """
    metadata = calculate_pagination_metadata(total, pagination)
    
    return PaginatedResponse(
        items=items,
        total=metadata.total,
        page=metadata.page,
        size=metadata.size,
        pages=metadata.pages,
        has_next=metadata.has_next,
        has_prev=metadata.has_prev
    )


def paginate_query(
    query: SQLQuery,
    pagination: PaginationParams,
    search_term: Optional[str] = None,
    search_fields: Optional[List[Any]] = None
) -> tuple[List[Any], int]:
    """
    Complete pagination workflow for a query.
    
    Args:
        query: Base SQLAlchemy query
        pagination: Pagination parameters
        search_term: Optional search string
        search_fields: Optional list of fields to search in
        
    Returns:
        Tuple of (items, total_count)
    """
    # Apply search if provided
    if search_term and search_fields:
        query = apply_search(query, search_term, search_fields)
    
    # Get total count before pagination
    total = query.count()
    
    # Apply pagination
    items = apply_pagination(query, pagination).all()
    
    return items, total