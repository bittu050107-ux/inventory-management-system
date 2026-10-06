"""
Application DTOs: Category
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Pydantic schemas for category requests and responses.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class CategoryCreateRequest(BaseModel):
    """Payload for creating a new category."""
    name: str = Field(
        ...,
        min_length=1,
        max_length=150,
        description="Category name (unique, non-empty)",
        example="Electronics",
    )
    description: Optional[str] = Field(
        default=None,
        description="Optional category description",
        example="Electronic devices and accessories",
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("Category name cannot be empty or whitespace only")
        return trimmed


class CategoryUpdateRequest(BaseModel):
    """Payload for updating an existing category."""
    name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=150,
        description="New category name (optional)",
        example="Consumer Electronics",
    )
    description: Optional[str] = Field(
        default=None,
        description="New category description (optional)",
        example="Updated description",
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: Optional[str]) -> Optional[str]:
        if value is not None:
            trimmed = value.strip()
            if not trimmed:
                raise ValueError("Category name cannot be empty or whitespace only")
            return trimmed
        return value


class CategoryResponse(BaseModel):
    """Response DTO for category data."""
    id: int = Field(..., description="Unique category ID")
    name: str = Field(..., description="Category name")
    description: Optional[str] = Field(default=None, description="Category description")
    created_at: Optional[datetime] = Field(default=None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(default=None, description="Last update timestamp")

    class Config:
        from_attributes = True
