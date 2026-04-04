import logging
import yfinance as yf
from typing import List
import pandas as pd
from foliotrack.domain.Portfolio import Portfolio
from foliotrack.domain.Security import Security
from foliotrack.utils.Currency import get_rate_between


class MarketService:
    """
    Service to fetch market data and update portfolio securities.
    Supports pluggable providers (yfinance).
    """

    def __init__(self, provider: str = "yfinance"):
        self.provider = provider.lower()
        if self.provider not in ["yfinance"]:
            logging.warning(
                f"Unknown provider '{self.provider}', defaulting to 'yfinance'"
            )
            self.provider = "yfinance"

    def update_prices(self, portfolio: Portfolio) -> None:
        """
        Update prices for all securities in the portfolio that have fill=True.
        Refreshes exchange rates as well.
        """
        for security in portfolio.securities.values():
            if security.fill:
                try:
                    self._update_security_price(security, portfolio.currency)
                except Exception as e:
                    logging.error(f"Failed to update {security.ticker}: {e}")

        # After prices are updated, recalculate portfolio stats
        portfolio.recalculate_shares()

    def get_historical_data(
        self, tickers: List[str], start_date: str, end_date: str
    ) -> pd.DataFrame:
        """
        Fetch historical closing prices for a list of tickers.
        Returns a DataFrame with tickers as columns and dates as index.
        """

        match self.provider:
            case "yfinance":
                return self._fetch_history_yfinance(tickers, start_date, end_date)
            case _:
                logging.warning(
                    f"Unknown provider '{self.provider}', defaulting to yfinance for historical data."
                )
                return self._fetch_history_yfinance(tickers, start_date, end_date)

    def _update_security_price(
        self, security: Security, portfolio_currency: str
    ) -> None:
        # 1. Fetch Price
        price, currency, name = self._fetch_market_data(security.ticker)

        if price is not None:
            security.price_in_security_currency = price
        if currency is not None:
            security.currency = currency
        if name is not None and security.name == "Unnamed security":
            security.name = name

        # 2. Update Exchange Rate
        if security.currency.lower() != portfolio_currency.lower():
            try:
                security.exchange_rate = float(
                    get_rate_between(
                        security.currency.upper(), portfolio_currency.upper()
                    )
                )
            except Exception as e:
                logging.error(
                    f"Could not get rate for {security.currency}->{portfolio_currency}: {e}"
                )
        else:
            security.exchange_rate = 1.0

        # 3. Compute Value
        security.price_in_portfolio_currency = round(
            float(security.price_in_security_currency * security.exchange_rate), 2
        )
        security.value = round(
            security.volume * security.price_in_portfolio_currency, 2
        )

    def _fetch_market_data(self, ticker: str):
        """
        Returns (price, currency, name).
        """
        match self.provider:
            case "yfinance":
                return self._fetch_yfinance(ticker)
            case _:
                logging.warning(
                    f"Unknown provider '{self.provider}', defaulting to yfinance for market data."
                )
                return self._fetch_yfinance(ticker)

    def _fetch_yfinance(self, ticker_symbol: str):
        try:
            ticker = yf.Ticker(ticker_symbol)
            info = ticker.info
            # Fallback logic from original code
            name = info.get("longName", "Unnamed Security")
            if name == "Unnamed Security":
                name = info.get("shortName", "Unnamed Security")

            return (info.get("regularMarketPrice"), info.get("currency", "EUR"), name)
        except Exception as e:
            logging.error(f"yfinance error for {ticker_symbol}: {e}")
            return None, None, None

    def _fetch_history_yfinance(
        self, tickers: List[str], start_date: str, end_date: str
    ) -> pd.DataFrame:

        stock = yf.Tickers(tickers)
        hist = stock.history(start=start_date, period="max", interval="1d")

        # Fill missing data with values from previous dates
        hist.ffill(inplace=True)
        return hist
