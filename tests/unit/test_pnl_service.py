"""Unit tests for PnL service."""

import pytest


class TestPnLService:
    """Tests for PnL calculation service."""

    def test_calculate_breakeven_with_entry_kimp(self):
        """Test breakeven calculation adds fee rate to entry kimp."""
        from src.dashboard_v2.services.pnl_service import calculate_breakeven

        entry_kimp = 3.50
        result = calculate_breakeven(entry_kimp)

        # Breakeven = entry_kimp + fee_rate (0.38%)
        expected = 3.50 + 0.38
        assert abs(result - expected) < 0.01

    def test_calculate_breakeven_zero_entry(self):
        """Test breakeven calculation with zero entry kimp."""
        from src.dashboard_v2.services.pnl_service import calculate_breakeven

        result = calculate_breakeven(0)

        # Breakeven = 0 + 0.38 = 0.38
        assert abs(result - 0.38) < 0.01

    def test_calculate_pnl_profitable(self):
        """Test PnL calculation in profitable scenario."""
        from src.dashboard_v2.services.pnl_service import calculate_pnl

        entry_kimp = 3.50
        current_kimp = 4.10  # Above breakeven (3.88)

        result = calculate_pnl(entry_kimp, current_kimp)

        assert result["entry_kimp"] == entry_kimp
        assert result["current_kimp"] == current_kimp
        assert result["kimp_profit"] == 0.60  # 4.10 - 3.50
        assert result["is_profitable"] is True
        assert result["breakeven_kimp"] == pytest.approx(3.88, abs=0.01)

    def test_calculate_pnl_loss(self):
        """Test PnL calculation in loss scenario."""
        from src.dashboard_v2.services.pnl_service import calculate_pnl

        entry_kimp = 3.50
        current_kimp = 3.60  # Below breakeven (3.88)

        result = calculate_pnl(entry_kimp, current_kimp)

        assert result["is_profitable"] is False
        assert result["net_profit"] < 0

    def test_is_profitable_above_breakeven(self):
        """Test is_profitable returns True when current > breakeven."""
        from src.dashboard_v2.services.pnl_service import is_profitable

        assert is_profitable(entry_kimp=3.50, current_kimp=4.00) is True

    def test_is_profitable_below_breakeven(self):
        """Test is_profitable returns False when current < breakeven."""
        from src.dashboard_v2.services.pnl_service import is_profitable

        assert is_profitable(entry_kimp=3.50, current_kimp=3.60) is False

    def test_is_profitable_at_breakeven(self):
        """Test is_profitable at exact breakeven point."""
        from src.dashboard_v2.services.pnl_service import is_profitable

        # At breakeven (3.50 + 0.38 = 3.88), should be True (>=)
        assert is_profitable(entry_kimp=3.50, current_kimp=3.88) is True

    @pytest.mark.asyncio
    async def test_get_pnl_data_no_position(self):
        """Test get_pnl_data with no open position."""
        from src.dashboard_v2.services.pnl_service import get_pnl_data

        result = await get_pnl_data()

        # Should return data even without position
        assert result is not None
        assert "has_position" in result
