import pytest
import pandas as pd
import numpy as np
from foliotrack.domain.Portfolio import Portfolio
from foliotrack.services.MarketService import MarketService
from foliotrack.services.StatisticsService import StatisticsService
from foliotrack.statistics.metrics import TotalReturn, CAGR, MaxDrawdown, DailySharpe


class MockMarketService(MarketService):
    def get_historical_data(self, tickers, start_date):
        # Create a mock dataframe of prices for 10 days
        dates = pd.date_range(start=start_date, periods=10, freq="D")

        # Security A: 10, 11, 12, 13, 14, 15, 16, 17, 18, 19
        prices_A = np.arange(10, 20, dtype=float)
        # Security B: 100, 105, 110, 108, 106, 110, 115, 120, 118, 115
        prices_B = [
            100.0,
            105.0,
            110.0,
            108.0,
            106.0,
            110.0,
            115.0,
            120.0,
            118.0,
            115.0,
        ]
        # Benchmark
        prices_Bench = np.arange(100, 110, dtype=float)

        df = pd.DataFrame(
            {"A": prices_A, "B": prices_B, "^GSPC": prices_Bench}, index=dates
        )
        return {"Close": df}


def test_time_weighted_return():
    # Setup
    portfolio = Portfolio("Test")

    # Day 1 (index 0): Buy 10 units of A at 10 (Value = 100)
    # Day 5 (index 4): Buy 1 unit of B at 106 (Value = 106)

    # For dates we just use strings matching the generated date_range
    start_date = "2023-01-01"
    dates = pd.date_range(start=start_date, periods=10, freq="D")
    date_1 = dates[0].strftime("%Y-%m-%d")
    date_5 = dates[4].strftime("%Y-%m-%d")

    portfolio.buy_security("A", 10, date=date_1)
    portfolio.buy_security("B", 1, date=date_5)

    market_service = MockMarketService()
    statistics_service = StatisticsService(market_service)

    returns, values = statistics_service._build_twr_series(portfolio, start_date)

    assert len(returns) == 10

    # Day 1 logic:
    # V_begin = 0
    # V_pre_trade = 0 (we held nothing before day 1)
    # ret = 0
    assert returns.iloc[0] == 0.0
    # V_end = 10 * 10 = 100
    assert values.iloc[0] == 100.0

    # Day 2 logic:
    # held 10 A. Price A goes 10 -> 11.
    # V_begin = 100
    # V_pre_trade = 10 * 11 = 110.
    # ret = 110 / 100 - 1 = 0.1
    # V_end = 110
    assert np.isclose(returns.iloc[1], 0.1)
    assert values.iloc[1] == 110.0

    # Day 5 logic:
    # held 10 A. Price A goes 13 -> 14.
    # V_begin = 10 * 13 = 130
    # V_pre_trade = 10 * 14 = 140
    # ret = 140 / 130 - 1 = 0.076923
    assert np.isclose(returns.iloc[4], 140 / 130 - 1)

    # Day 5 trade: Buy 1 B.
    # V_end = 10 * 14 + 1 * 106 = 140 + 106 = 246
    assert values.iloc[4] == 246.0

    # Day 6 logic:
    # held 10 A, 1 B.
    # Price A: 14 -> 15. Price B: 106 -> 110
    # V_begin = 246
    # V_pre_trade = 10 * 15 + 1 * 110 = 150 + 110 = 260
    # ret = 260 / 246 - 1 = 0.05691
    assert np.isclose(returns.iloc[5], 260 / 246 - 1)
    assert values.iloc[5] == 260.0


def test_statistics_calculation():
    portfolio = Portfolio("Test")
    start_date = "2023-01-01"
    dates = pd.date_range(start=start_date, periods=10, freq="D")
    portfolio.buy_security("A", 10, date=dates[0].strftime("%Y-%m-%d"))

    market_service = MockMarketService()
    statistics_service = StatisticsService(market_service)

    metrics = [TotalReturn(), CAGR(), MaxDrawdown(), DailySharpe()]
    results = statistics_service.compute_statistics(
        portfolio, metrics=metrics, start_date=start_date
    )

    # Security A goes from 10 to 19 over 10 days.
    # Total return = 19/10 - 1 = 0.9 (90%)
    assert np.isclose(results["Total Return"], 0.9)
    # Price only goes up, so max drawdown is 0
    assert np.isclose(results["Max Drawdown"], 0.0)
    # Sharpe ratio should be positive
    assert results["Daily Sharpe Ratio"] > 0
