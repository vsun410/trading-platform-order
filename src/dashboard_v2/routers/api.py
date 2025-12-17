"""API router for Dashboard V2.

Provides JSON API endpoints for dashboard data.
"""

from fastapi import APIRouter, HTTPException
from loguru import logger

from src.dashboard_v2.services import kimp_service, health_service, position_service, pnl_service, emergency_service

router = APIRouter(prefix="/api", tags=["api"])


@router.get("/kimp/current")
async def get_current_kimp():
    """Get current kimp rate data.

    Returns:
        Current kimp, BTC prices, and exchange rate
    """
    try:
        data = await kimp_service.get_current_kimp()
        if data is None:
            raise HTTPException(status_code=503, detail="Kimp data unavailable")
        return data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_current_kimp: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/kimp")
async def get_kimp_history(hours: int = 1):
    """Get kimp history for charting.

    Args:
        hours: Number of hours of history (default: 1)

    Returns:
        List of kimp data points
    """
    try:
        data = await kimp_service.get_kimp_history(hours=hours)
        return data
    except Exception as e:
        logger.error(f"Error in get_kimp_history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def get_health():
    """Get system health status.

    Returns:
        Health status for all services
    """
    try:
        data = await health_service.check_all()
        return data
    except Exception as e:
        logger.error(f"Error in get_health: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ticker")
async def get_ticker():
    """Get ticker data for marquee display.

    Returns:
        Aggregated ticker data (BTC, ETH, USD/KRW, KIMP)
    """
    try:
        data = await kimp_service.get_ticker_data()
        return data
    except Exception as e:
        logger.error(f"Error in get_ticker: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/position")
async def get_position():
    """Get current position with invested amounts.

    Returns:
        Position data with total invested KRW, Upbit, Binance amounts
    """
    try:
        data = await position_service.get_position_with_invested()
        return data
    except Exception as e:
        logger.error(f"Error in get_position: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pnl")
async def get_pnl():
    """Get PnL data with breakeven calculation.

    Returns:
        PnL data including breakeven kimp and profit status
    """
    try:
        data = await pnl_service.get_pnl_data()
        return data
    except Exception as e:
        logger.error(f"Error in get_pnl: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Emergency Stop Endpoints

@router.get("/emergency/status")
async def get_emergency_status():
    """Get current emergency stop status.

    Returns:
        Emergency stop status including active flag and metadata
    """
    try:
        data = await emergency_service.get_emergency_status()
        return data
    except Exception as e:
        logger.error(f"Error in get_emergency_status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/emergency/activate")
async def activate_emergency_stop(reason: str = None):
    """Activate emergency stop.

    Halts all automated trading immediately.

    Args:
        reason: Optional reason for activation

    Returns:
        Activation result with timestamp
    """
    try:
        data = await emergency_service.activate_emergency_stop(reason=reason)
        return data
    except Exception as e:
        logger.error(f"Error in activate_emergency_stop: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/emergency/deactivate")
async def deactivate_emergency_stop():
    """Deactivate emergency stop.

    Resumes automated trading.

    Returns:
        Deactivation result with timestamp
    """
    try:
        data = await emergency_service.deactivate_emergency_stop()
        return data
    except Exception as e:
        logger.error(f"Error in deactivate_emergency_stop: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Trade History Endpoint

@router.get("/trades")
async def get_trades(limit: int = 50):
    """Get recent trade history.

    Args:
        limit: Maximum number of trades to return (default: 50)

    Returns:
        List of recent trades
    """
    try:
        # TODO: Implement trade history service
        return {
            "trades": [],
            "total": 0,
            "limit": limit,
        }
    except Exception as e:
        logger.error(f"Error in get_trades: {e}")
        raise HTTPException(status_code=500, detail=str(e))
