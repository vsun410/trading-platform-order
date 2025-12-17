"""Unit tests for Kimp service."""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch


class TestKimpService:
    """Tests for Kimp data service."""

    @pytest.mark.asyncio
    async def test_get_current_kimp_returns_kimp_data(self):
        """Test that get_current_kimp returns current kimp rate."""
        from src.dashboard_v2.services.kimp_service import get_current_kimp

        result = await get_current_kimp()

        assert result is not None
        assert "kimp" in result
        assert "usd_krw" in result
        assert "btc_krw" in result
        assert "btc_usd" in result
        assert isinstance(result["kimp"], (int, float))

    @pytest.mark.asyncio
    async def test_get_kimp_history_returns_list(self):
        """Test that get_kimp_history returns a list of kimp data."""
        from src.dashboard_v2.services.kimp_service import get_kimp_history

        result = await get_kimp_history(hours=1)

        assert result is not None
        assert isinstance(result, list)
        # Each item should have timestamp and kimp
        if len(result) > 0:
            assert "timestamp" in result[0]
            assert "kimp" in result[0]

    @pytest.mark.asyncio
    async def test_get_current_kimp_handles_db_error(self):
        """Test that get_current_kimp handles database errors gracefully."""
        from src.dashboard_v2.services.kimp_service import get_current_kimp

        # Should return default/fallback data on error
        with patch(
            "src.dashboard_v2.services.kimp_service.get_supabase_client",
            side_effect=Exception("DB Error"),
        ):
            result = await get_current_kimp()
            # Should return None or default data on error
            assert result is None or "error" in result
