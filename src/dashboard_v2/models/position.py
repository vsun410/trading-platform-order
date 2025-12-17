"""Pydantic models for Position data."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class PositionData(BaseModel):
    """Position data with invested amounts."""

    # Basic position info
    quantity: float = Field(0, description="BTC quantity")
    entry_price_krw: float = Field(0, description="Entry price in KRW (Upbit)")
    entry_price_usd: float = Field(0, description="Entry price in USD (Binance)")
    entry_kimp: float = Field(0, description="Entry kimchi premium (%)")

    # Current prices
    current_price_krw: Optional[float] = None
    current_price_usd: Optional[float] = None
    usd_krw: float = Field(0, description="USD/KRW exchange rate")

    # Invested amounts (calculated)
    total_invested_krw: float = Field(0, description="Total invested in KRW")
    upbit_invested: float = Field(0, description="Upbit invested amount in KRW")
    binance_invested_krw: float = Field(0, description="Binance invested converted to KRW")

    # Position metadata
    status: str = Field("closed", description="Position status: open/closed")
    opened_at: Optional[datetime] = None
    holding_hours: float = Field(0, description="Hours since position opened")

    class Config:
        json_schema_extra = {
            "example": {
                "quantity": 0.1,
                "entry_price_krw": 145000000,
                "entry_price_usd": 100000,
                "entry_kimp": 3.57,
                "current_price_krw": 146000000,
                "current_price_usd": 100500,
                "usd_krw": 1400,
                "total_invested_krw": 28500000,
                "upbit_invested": 14500000,
                "binance_invested_krw": 14000000,
                "status": "open",
                "opened_at": "2025-12-17T10:00:00Z",
                "holding_hours": 2.5,
            }
        }


class PositionResponse(BaseModel):
    """API response for position endpoint."""

    has_position: bool = Field(..., description="Whether there is an open position")
    position: Optional[PositionData] = None
    total_invested_krw: float = Field(0, description="Total invested amount in KRW")
    positions: list[dict] = Field(default_factory=list, description="List of positions for table")
