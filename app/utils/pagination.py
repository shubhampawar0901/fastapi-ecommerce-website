"""
Pagination utilities for database queries
Provides consistent pagination across the application
"""

from typing import TypeVar, Generic, List, Optional
from pydantic import BaseModel, Field
from sqlalchemy.orm import Query
from math import ceil

from app.core.config import settings

T = TypeVar('T')


class PaginationParams(BaseModel):
    """
    Pagination parameters for API endpoints
    """
    page: int = Field(default=1, ge=1, description="Page number (1-based)")
    size: int = Field(
        default=settings.DEFAULT_PAGE_SIZE,
        ge=1,
        le=settings.MAX_PAGE_SIZE,
        description=f"Page size (max {settings.MAX_PAGE_SIZE})"
    )
    
    @property
    def offset(self) -> int:
        """Calculate offset for database query"""
        return (self.page - 1) * self.size
    
    @property
    def limit(self) -> int:
        """Get limit for database query"""
        return self.size


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Generic paginated response model
    """
    items: List[T]
    total: int
    page: int
    size: int
    pages: int
    has_next: bool
    has_prev: bool
    
    @classmethod
    def create(
        cls,
        items: List[T],
        total: int,
        pagination: PaginationParams
    ) -> "PaginatedResponse[T]":
        """
        Create paginated response from items and pagination params
        """
        pages = ceil(total / pagination.size) if total > 0 else 0
        
        return cls(
            items=items,
            total=total,
            page=pagination.page,
            size=pagination.size,
            pages=pages,
            has_next=pagination.page < pages,
            has_prev=pagination.page > 1
        )


def paginate_query(
    query: Query,
    pagination: PaginationParams
) -> tuple[List[T], int]:
    """
    Apply pagination to SQLAlchemy query
    
    Args:
        query: SQLAlchemy query object
        pagination: Pagination parameters
        
    Returns:
        Tuple of (items, total_count)
    """
    # Get total count
    total = query.count()
    
    # Apply pagination
    items = query.offset(pagination.offset).limit(pagination.limit).all()
    
    return items, total
