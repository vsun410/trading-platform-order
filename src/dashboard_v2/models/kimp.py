"""Pydantic models for Kimp data."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class KimpData(BaseModel):
    """Current kimp rate data."""

    kimp: float = Field(..., description="Current kimchi premium rate (%)")
    btc_krw: float = Field(..., description="BTC price in KRW (Upbit)")
    btc_usd: float = Field(..., description="BTC price in USD (Binance)")
    usd_krw: float = Field(..., description="USD/KRW exchange rate")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "kimp": 3.45,
                "btc_krw": 145000000,
                "btc_usd": 100000,
                "usd_krw": 1400,
                "timestamp": "2025-12-17T12:00:00Z",
            }
        }


class KimpHistoryItem(BaseModel):
    """Single item in kimp history."""

    timestamp: datetime
    kimp: float
    btc_krw: Optional[float] = None
    btc_usd: Optional[float] = None
    usd_krw: Optional[float] = None


class KimpHistoryResponse(BaseModel):
    """Response for kimp history endpoint."""

    data: list[KimpHistoryItem]
    count: int
    period_hours: int = 1
