"""Health check service.

Provides health status for all external services and dependencies.
"""

import asyncio
import time
from datetime import datetime
from typing import Optional

import httpx
from loguru import logger

from src.dashboard_v2.config import settings
from src.dashboard_v2.models.system import ServiceStatus, SystemHealthResponse


async def check_supabase() -> bool:
    """Check Supabase connection health.

    Returns:
        True if healthy, False otherwise
    """
    try:
        from supabase import create_client

        client = create_client(settings.supabase_url, settings.supabase_key)
        # Simple query to check connection
        client.table("kimp_1m").select("timestamp").limit(1).execute()
        return True
    except Exception as e:
        logger.warning(f"Supabase health check failed: {e}")
        return False


async def check_upbit() -> tuple[bool, Optional[float]]:
    """Check Upbit API health.

    Returns:
        Tuple of (is_healthy, latency_ms)
    """
    try:
        start = time.time()
        async with httpx.AsyncClient(timeout=settings.api_timeout) as client:
            response = await client.get("https://api.upbit.com/v1/ticker?markets=KRW-BTC")
            latency = (time.time() - start) * 1000

            if response.status_code == 200:
                return True, round(latency, 2)

        return False, None
    except Exception as e:
        logger.warning(f"Upbit health check failed: {e}")
        return False, None


async def check_binance() -> tuple[bool, Optional[float]]:
    """Check Binance API health.

    Returns:
        Tuple of (is_healthy, latency_ms)
    """
    try:
        start = time.time()
        async with httpx.AsyncClient(timeout=settings.api_timeout) as client:
            response = await client.get("https://api.binance.com/api/v3/ping")
            latency = (time.time() - start) * 1000

            if response.status_code == 200:
                return True, round(latency, 2)

        return False, None
    except Exception as e:
        logger.warning(f"Binance health check failed: {e}")
        return False, None


async def check_all() -> dict:
    """Check health of all services.

    Returns:
        SystemHealthResponse dict with overall status and per-service status
    """
    now = datetime.utcnow()

    # Run all checks in parallel
    supabase_task = asyncio.create_task(check_supabase())
    upbit_task = asyncio.create_task(check_upbit())
    binance_task = asyncio.create_task(check_binance())

    supabase_healthy = await supabase_task
    upbit_healthy, upbit_latency = await upbit_task
    binance_healthy, binance_latency = await binance_task

    services = {
        "supabase": {
            "name": "supabase",
            "healthy": supabase_healthy,
            "latency_ms": None,
            "error": None if supabase_healthy else "Connection failed",
            "last_check": now.isoformat(),
        },
        "upbit": {
            "name": "upbit",
            "healthy": upbit_healthy,
            "latency_ms": upbit_latency,
            "error": None if upbit_healthy else "API unreachable",
            "last_check": now.isoformat(),
        },
        "binance": {
            "name": "binance",
            "healthy": binance_healthy,
            "latency_ms": binance_latency,
            "error": None if binance_healthy else "API unreachable",
            "last_check": now.isoformat(),
        },
    }

    # Determine overall status
    all_healthy = all(s["healthy"] for s in services.values())
    any_healthy = any(s["healthy"] for s in services.values())

    if all_healthy:
        status = "healthy"
    elif any_healthy:
        status = "degraded"
    else:
        status = "unhealthy"

    return {
        "status": status,
        "services": services,
        "timestamp": now.isoformat(),
    }
