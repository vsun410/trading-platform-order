"""Kimp data service.

Handles fetching and calculating kimchi premium (김프) data from Supabase.
"""

from datetime import datetime, timedelta
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


async def get_current_kimp() -> Optional[dict]:
    """Get current kimp rate data.

    Returns:
        dict with kimp, btc_krw, btc_usd, usd_krw, timestamp
        None if error occurs
    """
    try:
        client = await get_supabase_client()

        # Get latest kimp data from kimp_1m table
        response = (
            client.table("kimp_1m")
            .select("*")
            .order("timestamp", desc=True)
            .limit(1)
            .execute()
        )

        if response.data and len(response.data) > 0:
            data = response.data[0]
            return {
                "kimp": data.get("kimp", 0),
                "btc_krw": data.get("btc_krw", 0),
                "btc_usd": data.get("btc_usd", 0),
                "usd_krw": data.get("usd_krw", 0),
                "timestamp": data.get("timestamp"),
            }

        logger.warning("No kimp data found in database")
        return None

    except Exception as e:
        logger.error(f"Error fetching current kimp: {e}")
        return None


async def get_kimp_history(hours: int = 1) -> list[dict]:
    """Get kimp history for the specified number of hours.

    Args:
        hours: Number of hours of history to fetch (default: 1)

    Returns:
        List of kimp data points with timestamp and kimp
    """
    try:
        client = await get_supabase_client()

        # Calculate time range
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)

        response = (
            client.table("kimp_1m")
            .select("timestamp, kimp, btc_krw, btc_usd, usd_krw")
            .gte("timestamp", start_time.isoformat())
            .lte("timestamp", end_time.isoformat())
            .order("timestamp", desc=False)
            .execute()
        )

        if response.data:
            return response.data

        logger.warning(f"No kimp history found for last {hours} hours")
        return []

    except Exception as e:
        logger.error(f"Error fetching kimp history: {e}")
        return []


def format_price_krw(price: float) -> str:
    """Format KRW price with comma separators."""
    if price >= 1_000_000:
        return f"{price:,.0f}"
    return f"{price:,.0f}"


def format_price_usd(price: float) -> str:
    """Format USD price with comma separators."""
    return f"{price:,.2f}"


async def get_ticker_data() -> dict:
    """Get aggregated ticker data for marquee display.

    Returns:
        dict with formatted BTC, ETH prices, USD/KRW, KIMP for ticker display
    """
    try:
        kimp_data = await get_current_kimp()
        kimp_history = await get_kimp_history(hours=1)

        # Calculate kimp change from 1 hour ago
        kimp_change = None
        if kimp_history and len(kimp_history) > 0 and kimp_data:
            first_kimp = kimp_history[0].get("kimp", 0)
            current_kimp = kimp_data.get("kimp", 0)
            kimp_change = current_kimp - first_kimp

        if kimp_data:
            btc_krw = kimp_data.get("btc_krw", 0)
            btc_usd = kimp_data.get("btc_usd", 0)
            usd_krw = kimp_data.get("usd_krw", 0)
            kimp = kimp_data.get("kimp", 0)

            # Format for display
            return {
                "btc_krw": format_price_krw(btc_krw),
                "btc_usdt": format_price_usd(btc_usd),
                "eth_krw": "-",  # TODO: Add ETH data when available
                "eth_usdt": "-",
                "usd_krw": f"{usd_krw:,.1f}",
                "kimp": f"{kimp:.2f}%",
                "kimp_change": round(kimp_change, 2) if kimp_change is not None else None,
                "timestamp": kimp_data.get("timestamp"),
            }

        return {
            "btc_krw": "-",
            "btc_usdt": "-",
            "eth_krw": "-",
            "eth_usdt": "-",
            "usd_krw": "-",
            "kimp": "-",
            "kimp_change": None,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error getting ticker data: {e}")
        return {
            "btc_krw": "-",
            "btc_usdt": "-",
            "eth_krw": "-",
            "eth_usdt": "-",
            "usd_krw": "-",
            "kimp": "-",
            "kimp_change": None,
            "error": str(e),
        }
