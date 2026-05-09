import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime

from foliotrack.domain.Portfolio import Portfolio
from foliotrack.services.MarketService import MarketService
from foliotrack.statistics.base import PortfolioStatistic
from foliotrack.statistics import DEFAULT_METRICS


class StatisticsService:
    """
    Service to calculate portfolio performance statistics using Time-Weighted Return (TWR)
    to handle mid-period cash flows (deposits and withdrawals).
    """

    def __init__(self, market_service: MarketService):
        self.market_service = market_service

    def compute_statistics(
        self,
        portfolio: Portfolio,
        metrics: Optional[List[PortfolioStatistic]] = None,
        start_date: Optional[str] = None,
        benchmark_ticker: str = "^STOXX50E",
    ) -> Dict[str, float]:
        """
        Computes the specified statistics for the given portfolio.

        Args:
            portfolio (Portfolio): The portfolio to analyze.
            metrics (List[PortfolioStatistic]): List of metric objects to compute. Defaults to DEFAULT_METRICS.
            start_date (str): Starting date for calculation (YYYY-MM-DD). If None, uses first transaction date.

        Returns:
            Dict[str, float]: Dictionary mapping metric names to their values.
        """
        if metrics is None:
            metrics = DEFAULT_METRICS

        if not portfolio.history:
            return {metric.name: 0.0 for metric in metrics}

        # 1. Build Time-Weighted Return series
        daily_returns, daily_values = self._build_twr_series(portfolio, start_date)

        # Fetch benchmark data
        first_date = daily_returns.index[0] if not daily_returns.empty else start_date
        benchmark_data = self.market_service.get_historical_data([benchmark_ticker], first_date)
        if "Close" in benchmark_data:
            benchmark_data = benchmark_data["Close"]
        
        benchmark_returns = pd.Series(dtype=float)
        if not benchmark_data.empty:
            # Drop timezone if any
            if benchmark_data.index.tz is not None:
                benchmark_data.index = benchmark_data.index.tz_localize(None)
            benchmark_prices = benchmark_data[benchmark_ticker].ffill()
            benchmark_returns = benchmark_prices.pct_change().dropna()

        # 2. Calculate each metric
        results = {}
        for metric in metrics:
            try:
                results[metric.name] = metric.calculate(
                    daily_returns=daily_returns, 
                    daily_values=daily_values,
                    benchmark_returns=benchmark_returns
                )
            except Exception as e:
                import logging

                logging.error(f"Error calculating {metric.name}: {e}")
                results[metric.name] = 0.0

        return results

    def _build_twr_series(self, portfolio: Portfolio, start_date: Optional[str] = None):
        """
        Builds the daily returns using Time-Weighted Return logic.
        Assumes all cash flows (buys/sells) are funded from external sources.
        Trades are assumed to execute at the closing price of the transaction day.
        """
        # Sort history by date
        sorted_history = sorted(portfolio.history, key=lambda x: x["date"])

        if start_date is None:
            start_date = sorted_history[0]["date"]

        # Get all unique tickers ever held
        tickers = list(set([tx["ticker"] for tx in portfolio.history]))

        # Fetch market data from start_date
        # historical_prices is a DataFrame with dates as index and tickers as columns
        historical_prices = self.market_service.get_historical_data(tickers, start_date)
        if "Close" in historical_prices:
            historical_prices = historical_prices["Close"]
        else:
            # Depending on yfinance behavior when 1 ticker vs multiple, make sure we have Close prices
            pass
            
        # If no data returned, return empty series
        if historical_prices.empty:
            return pd.Series(dtype=float), pd.Series(dtype=float)

        # Ensure index is datetime
        historical_prices.index = pd.to_datetime(historical_prices.index)
        
        # We need to localize or remove timezone to match with transaction dates
        if historical_prices.index.tz is not None:
            historical_prices.index = historical_prices.index.tz_localize(None)

        # Group transactions by date
        tx_by_date = {}
        for tx in sorted_history:
            dt = pd.to_datetime(tx["date"])
            if dt not in tx_by_date:
                tx_by_date[dt] = []
            tx_by_date[dt].append(tx)

        holdings = {ticker: 0.0 for ticker in tickers}
        daily_returns = []
        daily_values = []
        dates = []

        # Iterate through the historical dates
        for current_date in historical_prices.index:
            prices_t = historical_prices.loc[current_date].fillna(0)

            # 1. Calculate value of PREVIOUS day's holdings at CURRENT day's prices (Pre-trade value)
            v_pre_trade = sum(holdings[ticker] * prices_t.get(ticker, 0) for ticker in tickers)
            
            # 2. Get previous day's end value (Post-trade value of previous day)
            v_begin = daily_values[-1] if daily_values else 0.0

            # 3. Calculate daily return
            if v_begin > 0:
                ret = (v_pre_trade / v_begin) - 1
            else:
                # If we had 0 value yesterday, the return is 0 (we are just injecting cash today)
                ret = 0.0

            daily_returns.append(ret)
            dates.append(current_date)

            # 4. Process trades for the current day
            # User instruction: "Assume that the cash comes from an external source."
            if current_date in tx_by_date:
                for tx in tx_by_date[current_date]:
                    holdings[tx["ticker"]] += tx["volume"]

            # 5. Calculate value of CURRENT holdings at CURRENT day's prices (Post-trade value)
            v_end = sum(holdings[ticker] * prices_t.get(ticker, 0) for ticker in tickers)
            daily_values.append(v_end)

        returns_series = pd.Series(daily_returns, index=dates)
        values_series = pd.Series(daily_values, index=dates)

        return returns_series, values_series
