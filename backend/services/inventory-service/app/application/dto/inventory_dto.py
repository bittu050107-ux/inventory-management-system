"""
Application DTOs: inventory_dto.py (Inventory Service)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Pydantic schemas for stock movement requests and inventory responses.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class StockInRequest(BaseModel):
    """Payload for POST /inventory/stock-in."""
    product_id: int = Field(
        ...,
        gt=0,
        description="ID of the product receiving stock",
        example=1,
    )
    quantity: int = Field(
        ...,
        gt=0,
        description="Units of stock to add (must be greater than 0)",
        example=20,
    )
    reference: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Transaction reference code (e.g. PO-1001)",
        example="PO-1001",
    )
    notes: Optional[str] = Field(
        default=None,
        description="Optional explanatory notes",
        example="New stock received",
    )


class StockOutRequest(BaseModel):
    """Payload for POST /inventory/stock-out."""
    product_id: int = Field(
        ...,
        gt=0,
        description="ID of the product dispatching stock",
        example=1,
    )
    quantity: int = Field(
        ...,
        gt=0,
        description="Units of stock to dispatch (must be greater than 0)",
        example=5,
    )
    reference: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Transaction reference code (e.g. SALE-1001)",
        example="SALE-1001",
    )
    notes: Optional[str] = Field(
        default=None,
        description="Optional explanatory notes",
        example="Product sold",
    )


class StockAdjustRequest(BaseModel):
    """Payload for POST /inventory/adjust."""
    product_id: int = Field(
        ...,
        gt=0,
        description="ID of the product being adjusted",
        example=1,
    )
    quantity: int = Field(
        ...,
        ge=0,
        description="New total stock quantity (cannot be negative)",
        example=50,
    )
    notes: Optional[str] = Field(
        default=None,
        description="Reason for inventory correction",
        example="Physical stock correction",
    )


class InventoryResponse(BaseModel):
    """Inventory item response DTO."""
    id: int = Field(..., description="Unique inventory record ID")
    product_id: int = Field(..., description="Referenced Product ID")
    quantity: int = Field(..., description="Current available stock")
    reorder_level: int = Field(..., description="Minimum reorder threshold")
    created_at: Optional[datetime] = Field(default=None, description="Record creation time")
    updated_at: Optional[datetime] = Field(default=None, description="Last update time")

    class Config:
        from_attributes = True


class LowStockResponse(BaseModel):
    """DTO for low stock alerts (GET /inventory/low-stock)."""
    product_id: int = Field(..., description="Product ID")
    quantity: int = Field(..., description="Current stock level")
    reorder_level: int = Field(..., description="Configured reorder threshold")

    class Config:
        from_attributes = True


class StockTransactionResponse(BaseModel):
    """DTO for stock transaction audit history."""
    id: int = Field(..., description="Transaction ID")
    product_id: int = Field(..., description="Product ID")
    transaction_type: str = Field(..., description="Movement type: IN, OUT, or ADJUSTMENT")
    quantity: int = Field(..., description="Units moved")
    reference: Optional[str] = Field(default=None, description="External reference")
    notes: Optional[str] = Field(default=None, description="Audit notes")
    created_by: str = Field(..., description="User ID who executed the transaction")
    created_at: Optional[datetime] = Field(default=None, description="Transaction timestamp")

    class Config:
        from_attributes = True
