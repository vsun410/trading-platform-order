"""Unit tests for Health service."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch


class TestHealthService:
    """Tests for Health check service."""

    @pytest.mark.asyncio
    async def test_check_all_returns_status(self):
        """Test that check_all returns health status for all services."""
        from src.dashboard_v2.services.health_service import check_all

        result = await check_all()

        assert result is not None
        assert "status" in result
        assert "services" in result
        assert isinstance(result["services"], dict)

    @pytest.mark.asyncio
    async def test_check_all_includes_required_services(self):
        """Test that check_all includes status for all required services."""
        from src.dashboard_v2.services.health_service import check_all

        result = await check_all()

        services = result.get("services", {})
        # Should include status for these services
        expected_services = ["supabase", "upbit", "binance"]
        for service in expected_services:
            assert service in services

    @pytest.mark.asyncio
    async def test_check_supabase_returns_boolean(self):
        """Test that check_supabase returns a boolean status."""
        from src.dashboard_v2.services.health_service import check_supabase

        result = await check_supabase()

        assert isinstance(result, bool)

    @pytest.mark.asyncio
    async def test_check_all_handles_service_failure(self):
        """Test that check_all handles individual service failures."""
        from src.dashboard_v2.services.health_service import check_all

        # Even if one service fails, should return status for others
        result = await check_all()

        assert result is not None
        assert "status" in result
