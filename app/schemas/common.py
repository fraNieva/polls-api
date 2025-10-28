"""
Common schemas shared across the API.

This module contains reusable schemas that can be used by multiple endpoints.
"""

from typing import TypeVar, Generic, List
from pydantic import BaseModel, Field, ConfigDict


# Generic type for paginated responses
T = TypeVar('T')


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response schema that can be used for any item type"""
    items: List[T] = Field(..., description="List of items for current page")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number") 
    size: int = Field(..., description="Items per page")
    pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there are more pages")
    has_prev: bool = Field(..., description="Whether there are previous pages")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "items": [],
                "total": 25,
                "page": 1,
                "size": 10,
                "pages": 3,
                "has_next": True,
                "has_prev": False
            }
        }
    )