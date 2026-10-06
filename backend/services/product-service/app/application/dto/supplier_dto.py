"""
Application DTOs: Supplier
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Pydantic schemas for supplier requests and responses.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class SupplierCreateRequest(BaseModel):
    """Payload for creating a new supplier."""
    name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Supplier name (required, non-empty)",
        example="ABC Suppliers",
    )
    email: Optional[str] = Field(
        default=None,
        description="Supplier contact email",
        example="abc@example.com",
    )
    phone: Optional[str] = Field(
        default=None,
        description="Supplier contact phone",
        example="9876543210",
    )
    address: Optional[str] = Field(
        default=None,
        description="Supplier physical address",
        example="Delhi",
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("Supplier name cannot be empty or whitespace only")
        return trimmed


class SupplierUpdateRequest(BaseModel):
    """Payload for updating an existing supplier."""
    name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=200,
        description="New supplier name",
        example="ABC Global Suppliers",
    )
    email: Optional[str] = Field(
        default=None,
        description="New supplier email",
        example="contact@abcsuppliers.com",
    )
    phone: Optional[str] = Field(
        default=None,
        description="New supplier phone",
        example="+91-9876543210",
    )
    address: Optional[str] = Field(
        default=None,
        description="New supplier address",
        example="Sector 18, Noida",
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: Optional[str]) -> Optional[str]:
        if value is not None:
            trimmed = value.strip()
            if not trimmed:
                raise ValueError("Supplier name cannot be empty or whitespace only")
            return trimmed
        return value


class SupplierResponse(BaseModel):
    """Response DTO for supplier data."""
    id: int = Field(..., description="Unique supplier ID")
    name: str = Field(..., description="Supplier name")
    email: Optional[str] = Field(default=None, description="Contact email")
    phone: Optional[str] = Field(default=None, description="Contact phone")
    address: Optional[str] = Field(default=None, description="Physical address")
    created_at: Optional[datetime] = Field(default=None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(default=None, description="Last update timestamp")

    class Config:
        from_attributes = True
