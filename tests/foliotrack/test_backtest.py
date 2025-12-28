from foliotrack.Backtest import run_backtest
from foliotrack.Portfolio import Portfolio


def test_run_backtest():
    """
    Tests the run_backtest function in Backtest module.

    Verifies that backtest runs without errors and returns a result object.
    """
    portfolio = Portfolio("Test Portfolio", currency="USD")
    portfolio.buy_security("AAPL", volume=10.0, price=150.0, fill=True)
    portfolio.set_target_share("AAPL", 1.0)

    result = run_backtest(portfolio, start_date="2020-01-01", end_date="2021-01-01")
    assert result is not None
    assert hasattr(result, "display")  # Check if result has display method
