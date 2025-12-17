"""Unit tests for Emergency Stop service."""

import pytest
from unittest.mock import AsyncMock, patch


class TestEmergencyService:
    """Tests for Emergency Stop functionality."""

    @pytest.mark.asyncio
    async def test_activate_emergency_stop(self):
        """Test activating emergency stop sets flag to True."""
        from src.dashboard_v2.services.emergency_service import activate_emergency_stop

        result = await activate_emergency_stop()

        assert result["success"] is True
        assert result["active"] is True

    @pytest.mark.asyncio
    async def test_deactivate_emergency_stop(self):
        """Test deactivating emergency stop sets flag to False."""
        from src.dashboard_v2.services.emergency_service import deactivate_emergency_stop

        result = await deactivate_emergency_stop()

        assert result["success"] is True
        assert result["active"] is False

    @pytest.mark.asyncio
    async def test_get_emergency_status(self):
        """Test getting emergency status returns current state."""
        from src.dashboard_v2.services.emergency_service import (
            get_emergency_status,
            activate_emergency_stop,
            deactivate_emergency_stop,
        )

        # Test initial state
        status = await get_emergency_status()
        assert "active" in status

        # Test after activation
        await activate_emergency_stop()
        status = await get_emergency_status()
        assert status["active"] is True

        # Test after deactivation
        await deactivate_emergency_stop()
        status = await get_emergency_status()
        assert status["active"] is False

    @pytest.mark.asyncio
    async def test_activate_records_timestamp(self):
        """Test that activation records a timestamp."""
        from src.dashboard_v2.services.emergency_service import (
            activate_emergency_stop,
            get_emergency_status,
        )

        await activate_emergency_stop()
        status = await get_emergency_status()

        assert "activated_at" in status
        assert status["activated_at"] is not None

    @pytest.mark.asyncio
    async def test_activate_records_reason(self):
        """Test that activation can record a reason."""
        from src.dashboard_v2.services.emergency_service import (
            activate_emergency_stop,
            get_emergency_status,
        )

        await activate_emergency_stop(reason="Manual activation")
        status = await get_emergency_status()

        assert status.get("reason") == "Manual activation"

    @pytest.mark.asyncio
    async def test_double_activation_is_idempotent(self):
        """Test that activating twice doesn't cause errors."""
        from src.dashboard_v2.services.emergency_service import (
            activate_emergency_stop,
            get_emergency_status,
        )

        # Activate twice
        await activate_emergency_stop()
        result = await activate_emergency_stop()

        assert result["success"] is True

        status = await get_emergency_status()
        assert status["active"] is True

    @pytest.mark.asyncio
    async def test_double_deactivation_is_idempotent(self):
        """Test that deactivating twice doesn't cause errors."""
        from src.dashboard_v2.services.emergency_service import (
            deactivate_emergency_stop,
            get_emergency_status,
        )

        # Deactivate twice
        await deactivate_emergency_stop()
        result = await deactivate_emergency_stop()

        assert result["success"] is True

        status = await get_emergency_status()
        assert status["active"] is False
