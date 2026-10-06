"""
Application DTOs: Product
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Pydantic schemas for product requests and responses.
Includes strict validation for non-empty names, SKUs, and positive prices.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class ProductCreateRequest(BaseModel):
    """Payload for creating a new product."""
    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Product name (required, non-empty)",
        example="Wireless Mouse",
    )
    sku: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Stock Keeping Unit (unique identifier)",
        example="WM-001",
    )
    description: Optional[str] = Field(
        default=None,
        description="Product description",
        example="2.4GHz wireless mouse",
    )
    price: float = Field(
        ...,
        ge=0.0,
        description="Product price (must be greater than or equal to 0)",
        example=799.99,
    )
    category_id: int = Field(
        ...,
        gt=0,
        description="Foreign key ID referencing category",
        example=1,
    )
    supplier_id: int = Field(
        ...,
        gt=0,
        description="Foreign key ID referencing supplier",
        example=1,
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("Product name cannot be empty or whitespace only")
        return trimmed

    @field_validator("sku")
    @classmethod
    def validate_sku(cls, value: str) -> str:
        trimmed = value.strip().upper()
        if not trimmed:
            raise ValueError("Product SKU cannot be empty or whitespace only")
        return trimmed


class ProductUpdateRequest(BaseModel):
    """Payload for updating an existing product."""
    name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=255,
        description="Updated product name",
        example="Wireless Mouse Pro",
    )
    sku: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=100,
        description="Updated product SKU",
        example="WM-002",
    )
    description: Optional[str] = Field(
        default=None,
        description="Updated description",
        example="Rechargeable wireless mouse",
    )
    price: Optional[float] = Field(
        default=None,
        ge=0.0,
        description="Updated price",
        example=899.99,
    )
    category_id: Optional[int] = Field(
        default=None,
        gt=0,
        description="Updated category ID",
        example=1,
    )
    supplier_id: Optional[int] = Field(
        default=None,
        gt=0,
        description="Updated supplier ID",
        example=1,
    )
    is_active: Optional[bool] = Field(
        default=None,
        description="Product active status",
        example=True,
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: Optional[str]) -> Optional[str]:
        if value is not None:
            trimmed = value.strip()
            if not trimmed:
                raise ValueError("Product name cannot be empty or whitespace only")
            return trimmed
        return value

    @field_validator("sku")
    @classmethod
    def validate_sku(cls, value: Optional[str]) -> Optional[str]:
        if value is not None:
            trimmed = value.strip().upper()
            if not trimmed:
                raise ValueError("Product SKU cannot be empty or whitespace only")
            return trimmed
        return value


class ProductResponse(BaseModel):
    """Response DTO for product data."""
    id: int = Field(..., description="Unique product ID")
    name: str = Field(..., description="Product name")
    sku: str = Field(..., description="Product SKU")
    description: Optional[str] = Field(default=None, description="Product description")
    price: float = Field(..., description="Product price")
    category_id: int = Field(..., description="Category ID")
    supplier_id: int = Field(..., description="Supplier ID")
    is_active: bool = Field(default=True, description="Active status")
    created_at: Optional[datetime] = Field(default=None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(default=None, description="Last update timestamp")

    class Config:
        from_attributes = True
