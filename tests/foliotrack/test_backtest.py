from foliotrack.services.BacktestService import BacktestService
from foliotrack.domain.Portfolio import Portfolio


def test_run_backtest():
    """
    Tests the run_backtest function in Backtest module.
    """
    portfolio = Portfolio("Test Portfolio", currency="USD")
    # Requires existing ticker for backtest (bt uses Yahoo)
    # Using AAPL
    portfolio.buy_security("AAPL", volume=10.0, price=150.0, fill=False)
    # fill=False because we don't have MarketService here, creating raw.
    portfolio.set_target_share("AAPL", 1.0)

    backtester = BacktestService()
    try:
        result = backtester.run_backtest(
            portfolio, start_date="2020-01-01", end_date="2021-01-01"
        )
        assert result is not None
        assert hasattr(result, "display")
    except Exception as e:
        # If bt fails due to network/dependency, we should know.
        raise
