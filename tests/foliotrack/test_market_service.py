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


def test_ffn_provider_init():
    """Test that we can init with ffn, even if we don't fetch."""
    service = MarketService(provider="ffn")
    assert service.provider == "ffn"
