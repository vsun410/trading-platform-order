"""Position service.

Handles fetching and calculating position data including invested amounts.
"""

from datetime import datetime
from typing import Optional

from loguru import logger

from src.dashboard_v2.config import settings


async def get_supabase_client():
    """Get Supabase client instance."""
    try:
        from supabase import create_client

        return create_client(settings.supabase_url, settings.supabase_key)
    except Exception as e:
        logger.error(f"Failed to create Supabase client: {e}")
        raise


def calculate_invested_amount(position: Optional[dict]) -> dict:
    """Calculate invested amounts from position data.

    Args:
        position: Position dict with quantity, entry_price_krw, entry_price_usd, usd_krw

    Returns:
        dict with total_invested_krw, upbit_invested, binance_invested_krw
    """
    if not position:
        return {
            "total_invested_krw": 0,
            "upbit_invested": 0,
            "binance_invested_krw": 0,
        }

    quantity = position.get("quantity", 0)
    entry_price_krw = position.get("entry_price_krw", 0)
    entry_price_usd = position.get("entry_price_usd", 0)
    usd_krw = position.get("usd_krw", 1400)  # Default exchange rate

    # Calculate invested amounts
    upbit_invested = quantity * entry_price_krw
    binance_invested_krw = quantity * entry_price_usd * usd_krw
    total_invested_krw = upbit_invested + binance_invested_krw

    return {
        "total_invested_krw": round(total_invested_krw, 0),
        "upbit_invested": round(upbit_invested, 0),
        "binance_invested_krw": round(binance_invested_krw, 0),
    }


async def get_position() -> Optional[dict]:
    """Get current open position from database.

    Returns:
        Position dict or None if no open position
    """
    try:
        client = await get_supabase_client()

        # Get open position from positions table
        response = (
            client.table("positions")
            .select("*")
            .eq("status", "open")
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )

        if response.data and len(response.data) > 0:
            position = response.data[0]

            # Calculate holding hours
            opened_at = position.get("created_at") or position.get("opened_at")
            if opened_at:
                try:
                    opened_dt = datetime.fromisoformat(opened_at.replace("Z", "+00:00"))
                    holding_hours = (datetime.now(opened_dt.tzinfo) - opened_dt).total_seconds() / 3600
                    position["holding_hours"] = round(holding_hours, 2)
                except Exception:
                    position["holding_hours"] = 0

            return position

        logger.info("No open position found")
        return None

    except Exception as e:
        logger.error(f"Error fetching position: {e}")
        return None


async def get_position_with_invested() -> dict:
    """Get position data with invested amount calculations.

    Returns:
        dict with position data and invested amounts
    """
    position = await get_position()
    invested = calculate_invested_amount(position)

    if position:
        # Get current USD/KRW rate for display
        try:
            from src.dashboard_v2.services.kimp_service import get_current_kimp

            kimp_data = await get_current_kimp()
            if kimp_data:
                position["usd_krw"] = kimp_data.get("usd_krw", 0)
                position["current_price_krw"] = kimp_data.get("btc_krw", 0)
                position["current_price_usd"] = kimp_data.get("btc_usd", 0)
        except Exception as e:
            logger.warning(f"Could not get current prices: {e}")

        return {
            "has_position": True,
            "position": position,
            **invested,
            "positions": [
                {
                    "symbol": "BTC",
                    "quantity": position.get("quantity", 0),
                    "entry_price": position.get("entry_price_krw", 0),
                    "current_price": position.get("current_price_krw", 0),
                    "pnl": 0,  # Will be calculated by pnl_service
                }
            ],
        }

    return {
        "has_position": False,
        "position": None,
        **invested,
        "positions": [],
    }
