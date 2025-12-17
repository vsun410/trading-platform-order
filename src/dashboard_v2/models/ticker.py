"""Pydantic models for ticker data."""

from typing import Optional

from pydantic import BaseModel, Field


class TickerItem(BaseModel):
    """Individual ticker item."""

    label: str = Field(..., description="Display label (e.g., 'BTC/KRW')")
    value: str = Field(..., description="Formatted value to display")
    change: Optional[float] = Field(None, description="Change percentage if applicable")
    is_positive: Optional[bool] = Field(None, description="Whether change is positive")


class TickerData(BaseModel):
    """Complete ticker data for marquee display."""

    btc_krw: str = Field(..., description="BTC/KRW price")
    btc_usdt: str = Field(..., description="BTC/USDT price")
    eth_krw: str = Field(..., description="ETH/KRW price")
    eth_usdt: str = Field(..., description="ETH/USDT price")
    usd_krw: str = Field(..., description="USD/KRW exchange rate")
    kimp: str = Field(..., description="Kimchi premium rate")
    kimp_change: Optional[float] = Field(None, description="Kimp change from 1h ago")

    class Config:
        json_schema_extra = {
            "example": {
                "btc_krw": "142,500,000",
                "btc_usdt": "98,500",
                "eth_krw": "4,850,000",
                "eth_usdt": "3,350",
                "usd_krw": "1,420",
                "kimp": "3.85%",
                "kimp_change": 0.12,
            }
        }


class TickerResponse(BaseModel):
    """API response for ticker endpoint."""

    items: list[TickerItem] = Field(default_factory=list, description="Ticker items")
    timestamp: str = Field(..., description="Data timestamp")
