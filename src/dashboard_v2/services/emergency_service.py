"""Emergency Stop service.

Handles emergency stop activation/deactivation for the trading system.
When activated, all automated trading is halted.
"""

from datetime import datetime, timezone
from typing import Optional

from loguru import logger

from src.dashboard_v2.config import settings

# In-memory state for emergency stop
# In production, this would be stored in Supabase for persistence across restarts
_emergency_state = {
    "active": False,
    "activated_at": None,
    "deactivated_at": None,
    "reason": None,
}


async def get_supabase_client():
    """Get Supabase client instance."""
    try:
        from supabase import create_client

        return create_client(settings.supabase_url, settings.supabase_key)
    except Exception as e:
        logger.error(f"Failed to create Supabase client: {e}")
        raise


async def get_emergency_status() -> dict:
    """Get current emergency stop status.

    Returns:
        dict with active status and metadata
    """
    try:
        # Try to get status from Supabase first
        client = await get_supabase_client()
        response = (
            client.table("system_state")
            .select("*")
            .eq("key", "emergency_stop")
            .limit(1)
            .execute()
        )

        if response.data and len(response.data) > 0:
            data = response.data[0]
            return {
                "active": data.get("value", {}).get("active", False),
                "activated_at": data.get("value", {}).get("activated_at"),
                "deactivated_at": data.get("value", {}).get("deactivated_at"),
                "reason": data.get("value", {}).get("reason"),
            }

    except Exception as e:
        logger.warning(f"Could not fetch emergency status from Supabase: {e}")

    # Fall back to in-memory state
    return {
        "active": _emergency_state["active"],
        "activated_at": _emergency_state["activated_at"],
        "deactivated_at": _emergency_state["deactivated_at"],
        "reason": _emergency_state["reason"],
    }


async def activate_emergency_stop(reason: Optional[str] = None) -> dict:
    """Activate emergency stop.

    Args:
        reason: Optional reason for activation

    Returns:
        dict with success status
    """
    global _emergency_state

    timestamp = datetime.now(timezone.utc).isoformat()

    # Update in-memory state
    _emergency_state["active"] = True
    _emergency_state["activated_at"] = timestamp
    _emergency_state["reason"] = reason or "Manual activation"

    try:
        # Try to persist to Supabase
        client = await get_supabase_client()

        # Upsert the emergency state
        response = client.table("system_state").upsert(
            {
                "key": "emergency_stop",
                "value": {
                    "active": True,
                    "activated_at": timestamp,
                    "reason": reason or "Manual activation",
                },
                "updated_at": timestamp,
            },
            on_conflict="key",
        ).execute()

        logger.warning(f"Emergency stop ACTIVATED: {reason or 'Manual activation'}")

        return {
            "success": True,
            "active": True,
            "activated_at": timestamp,
            "reason": reason or "Manual activation",
        }

    except Exception as e:
        logger.error(f"Error persisting emergency stop to Supabase: {e}")
        # Still return success since in-memory state is updated
        return {
            "success": True,
            "active": True,
            "activated_at": timestamp,
            "reason": reason or "Manual activation",
            "warning": "State not persisted to database",
        }


async def deactivate_emergency_stop() -> dict:
    """Deactivate emergency stop.

    Returns:
        dict with success status
    """
    global _emergency_state

    timestamp = datetime.now(timezone.utc).isoformat()

    # Update in-memory state
    _emergency_state["active"] = False
    _emergency_state["deactivated_at"] = timestamp
    _emergency_state["reason"] = None

    try:
        # Try to persist to Supabase
        client = await get_supabase_client()

        response = client.table("system_state").upsert(
            {
                "key": "emergency_stop",
                "value": {
                    "active": False,
                    "deactivated_at": timestamp,
                },
                "updated_at": timestamp,
            },
            on_conflict="key",
        ).execute()

        logger.info("Emergency stop DEACTIVATED")

        return {
            "success": True,
            "active": False,
            "deactivated_at": timestamp,
        }

    except Exception as e:
        logger.error(f"Error persisting emergency stop deactivation to Supabase: {e}")
        return {
            "success": True,
            "active": False,
            "deactivated_at": timestamp,
            "warning": "State not persisted to database",
        }


def is_emergency_active() -> bool:
    """Check if emergency stop is currently active.

    This is a synchronous function for use in trading logic.

    Returns:
        True if emergency stop is active
    """
    return _emergency_state["active"]
