"""Unit tests for Position service."""

import pytest
from unittest.mock import AsyncMock, patch


class TestPositionService:
    """Tests for Position service."""

    @pytest.mark.asyncio
    async def test_get_position_returns_position_data(self):
        """Test that get_position returns position data."""
        from src.dashboard_v2.services.position_service import get_position

        result = await get_position()

        # Should return dict or None
        assert result is None or isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_calculate_invested_amount_with_position(self):
        """Test invested amount calculation with position data."""
        from src.dashboard_v2.services.position_service import calculate_invested_amount

        position = {
            "quantity": 0.1,
            "entry_price_krw": 145000000,
            "entry_price_usd": 100000,
            "usd_krw": 1400,
        }

        result = calculate_invested_amount(position)

        assert "total_invested_krw" in result
        assert "upbit_invested" in result
        assert "binance_invested_krw" in result
        assert result["upbit_invested"] == 14500000  # 0.1 * 145000000
        assert result["binance_invested_krw"] == 14000000  # 0.1 * 100000 * 1400

    @pytest.mark.asyncio
    async def test_calculate_invested_amount_no_position(self):
        """Test invested amount calculation with no position."""
        from src.dashboard_v2.services.position_service import calculate_invested_amount

        result = calculate_invested_amount(None)

        assert result["total_invested_krw"] == 0
        assert result["upbit_invested"] == 0
        assert result["binance_invested_krw"] == 0

    @pytest.mark.asyncio
    async def test_get_position_with_invested_amount(self):
        """Test that get_position_with_invested returns complete data."""
        from src.dashboard_v2.services.position_service import get_position_with_invested

        result = await get_position_with_invested()

        assert result is not None
        assert "total_invested_krw" in result
