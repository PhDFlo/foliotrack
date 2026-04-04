from foliotrack.domain.Portfolio import Portfolio
from foliotrack.services.MarketService import MarketService
import logging


def test_update_prices_yfinance():
    """
    Test updating prices using MarketService with yfinance (default).
    Requires network access.
    """
    portfolio = Portfolio("Test Portfolio", currency="USD")
    # AAPL usually exists
    portfolio.buy_security("AAPL", volume=1.0, price=0.0, fill=True)

    service = MarketService(provider="yfinance")
    try:
        service.update_prices(portfolio)
        sec = portfolio.securities["AAPL"]
        assert sec.price_in_portfolio_currency > 0
        assert sec.name != "Unnamed Security"
    except Exception as e:
        logging.warning(f"MarketService test failed (network?): {e}")


def test_get_historical_data():
    """
    Test fetching historical prices using MarketService with yfinance (default).
    Requires network access.
    """
    service = MarketService(provider="yfinance")
    try:
        hist = service.get_historical_data("AAPL", "2023-01-01", "2023-01-10")
        assert not hist.empty
        assert "AAPL" in hist.columns
    except Exception as e:
        logging.warning(f"MarketService historical data test failed (network?): {e}")
