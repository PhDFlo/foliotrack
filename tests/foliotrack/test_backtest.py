from unittest.mock import MagicMock
import pytest
import pandas as pd
from foliotrack.services.BacktestService import BacktestService
from foliotrack.domain.Portfolio import Portfolio
from foliotrack.services.MarketService import MarketService


def test_run_backtest():
    """
    Tests the run_backtest function in Backtest module.
    """
    portfolio = Portfolio("Test Portfolio", currency="USD")
    # Using AAPL
    portfolio.buy_security("AAPL", volume=10.0, price=150.0, fill=False)
    portfolio.set_target_share("AAPL", 1.0)

    # Mock MarketService
    market_service = MagicMock(spec=MarketService)

    # Mock return data for get_historical_data
    # Use a price doubling scenario: 100 on Jan 1st, 200 on Jan 1st next year
    dates = pd.date_range(start="2020-01-01", end="2021-01-01", freq="D")
    # Linear increase from 100 to 200
    prices = [100.0 + (i * 100.0 / (len(dates) - 1)) for i in range(len(dates))]
    data = pd.DataFrame({"AAPL": prices}, index=dates)
    market_service.get_historical_data.return_value = data

    backtester = BacktestService()

    result = backtester.run_backtest(
        portfolio, market_service, start_date="2020-01-01", end_date="2021-01-01"
    )

    assert result is not None
    assert hasattr(result, "display")

    # Verify the results reflect the 100% price increase
    # bt.Result.stats is a DataFrame
    total_return = result.stats.loc["total_return"].iloc[0]
    assert total_return > 0
    assert total_return == pytest.approx(1.0, 0.05)  # Doubling should be ~100% return

    # Check that it has some stats
    assert "total_return" in result.stats.index
    assert "cagr" in result.stats.index

    # Verify call
    market_service.get_historical_data.assert_called_once()
