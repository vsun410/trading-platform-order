"""Pydantic models for PnL (Profit and Loss) data."""

from typing import Optional

from pydantic import BaseModel, Field


class PnLData(BaseModel):
    """PnL calculation data."""

    entry_kimp: float = Field(0, description="Entry kimchi premium (%)")
    current_kimp: float = Field(0, description="Current kimchi premium (%)")
    kimp_profit: float = Field(0, description="Kimp profit/loss (%)")
    fee_rate: float = Field(0.38, description="Total fee rate (%)")
    net_profit: float = Field(0, description="Net profit after fees (%)")
    breakeven_kimp: float = Field(0, description="Breakeven kimchi premium (%)")
    is_profitable: bool = Field(False, description="Whether current position is profitable")

    class Config:
        json_schema_extra = {
            "example": {
                "entry_kimp": 3.50,
                "current_kimp": 4.10,
                "kimp_profit": 0.60,
                "fee_rate": 0.38,
                "net_profit": 0.22,
                "breakeven_kimp": 3.88,
                "is_profitable": True,
            }
        }


class PnLResponse(BaseModel):
    """API response for PnL endpoint."""

    has_position: bool = Field(..., description="Whether there is an open position")
    pnl: Optional[PnLData] = None
    entry_kimp: Optional[float] = None
    current_kimp: Optional[float] = None
    kimp_profit: Optional[float] = None
    fee_rate: float = 0.38
    net_profit: Optional[float] = None
    breakeven_kimp: Optional[float] = None
    is_profitable: Optional[bool] = None
