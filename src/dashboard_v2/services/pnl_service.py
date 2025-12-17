"""PnL (Profit and Loss) service.

Handles breakeven calculation and profit/loss determination.
Fee rate is loaded from config (not hardcoded) per Constitution VIII.
"""

from typing import Optional

from loguru import logger

from src.dashboard_v2.config import settings


def calculate_breakeven(entry_kimp: float) -> float:
    """Calculate breakeven kimchi premium.

    Breakeven = Entry Kimp + Total Fee Rate

    Args:
        entry_kimp: Entry kimchi premium (%)

    Returns:
        Breakeven kimchi premium (%)
    """
    # Fee rate from config (not hardcoded)
    fee_rate_percent = settings.fee_rate * 100  # Convert 0.0038 to 0.38
    return entry_kimp + fee_rate_percent


def calculate_pnl(entry_kimp: float, current_kimp: float) -> dict:
    """Calculate profit/loss metrics.

    Args:
        entry_kimp: Entry kimchi premium (%)
        current_kimp: Current kimchi premium (%)

    Returns:
        dict with kimp_profit, net_profit, breakeven_kimp, is_profitable
    """
    # Fee rate from config
    fee_rate_percent = settings.fee_rate * 100

    # Kimp profit (long position: profit when current > entry)
    kimp_profit = current_kimp - entry_kimp

    # Net profit after fees
    net_profit = kimp_profit - fee_rate_percent

    # Breakeven point
    breakeven_kimp = calculate_breakeven(entry_kimp)

    # Is profitable (current >= breakeven)
    profitable = current_kimp >= breakeven_kimp

    return {
        "entry_kimp": entry_kimp,
        "current_kimp": current_kimp,
        "kimp_profit": round(kimp_profit, 2),
        "fee_rate": fee_rate_percent,
        "net_profit": round(net_profit, 2),
        "breakeven_kimp": round(breakeven_kimp, 2),
        "is_profitable": profitable,
    }


def is_profitable(entry_kimp: float, current_kimp: float) -> bool:
    """Check if position is profitable.

    Args:
        entry_kimp: Entry kimchi premium (%)
        current_kimp: Current kimchi premium (%)

    Returns:
        True if current >= breakeven, False otherwise
    """
    breakeven = calculate_breakeven(entry_kimp)
    return current_kimp >= breakeven


async def get_pnl_data() -> dict:
    """Get complete PnL data for current position.

    Returns:
        dict with PnL metrics or default values if no position
    """
    try:
        from src.dashboard_v2.services.position_service import get_position
        from src.dashboard_v2.services.kimp_service import get_current_kimp

        position = await get_position()
        kimp_data = await get_current_kimp()

        if not position:
            return {
                "has_position": False,
                "entry_kimp": None,
                "current_kimp": kimp_data.get("kimp") if kimp_data else None,
                "kimp_profit": None,
                "fee_rate": settings.fee_rate * 100,
                "net_profit": None,
                "breakeven_kimp": None,
                "is_profitable": None,
            }

        entry_kimp = position.get("entry_kimp", 0)
        current_kimp = kimp_data.get("kimp", 0) if kimp_data else 0

        pnl = calculate_pnl(entry_kimp, current_kimp)

        return {
            "has_position": True,
            **pnl,
        }

    except Exception as e:
        logger.error(f"Error getting PnL data: {e}")
        return {
            "has_position": False,
            "error": str(e),
        }
