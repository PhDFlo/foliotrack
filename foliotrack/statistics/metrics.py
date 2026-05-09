import pandas as pd
import ffn
import numpy as np
from datetime import datetime, timedelta
from typing import Optional

from .base import PortfolioStatistic

class TotalReturn(PortfolioStatistic):
    @property
    def name(self) -> str:
        return "Total Return"

    def calculate(self, daily_returns: pd.Series, daily_values: pd.Series = None, **kwargs) -> float:
        if daily_returns.empty:
            return 0.0
        return float((1 + daily_returns).prod() - 1)


class CAGR(PortfolioStatistic):
    @property
    def name(self) -> str:
        return "CAGR"

    def calculate(self, daily_returns: pd.Series, daily_values: pd.Series = None, **kwargs) -> float:
        if len(daily_returns) < 2:
            return 0.0
        # Create equity curve to use ffn
        equity = (1 + daily_returns).cumprod()
        # ffn's calc_cagr requires a pandas Series with DatetimeIndex
        return float(equity.calc_cagr())


class MaxDrawdown(PortfolioStatistic):
    @property
    def name(self) -> str:
        return "Max Drawdown"

    def calculate(self, daily_returns: pd.Series, daily_values: pd.Series = None, **kwargs) -> float:
        if daily_returns.empty:
            return 0.0
        equity = (1 + daily_returns).cumprod()
        return float(equity.calc_max_drawdown())


class DailySharpe(PortfolioStatistic):
    @property
    def name(self) -> str:
        return "Daily Sharpe Ratio"

    def calculate(self, daily_returns: pd.Series, daily_values: pd.Series = None, **kwargs) -> float:
        if daily_returns.empty or daily_returns.std() == 0:
            return 0.0
        # Risk free rate assumed 0 for simplicity
        return float(daily_returns.mean() / daily_returns.std())


class AnnualizedSharpe(PortfolioStatistic):
    @property
    def name(self) -> str:
        return "Annualized Sharpe Ratio"

    def calculate(self, daily_returns: pd.Series, daily_values: pd.Series = None, **kwargs) -> float:
        if daily_returns.empty or daily_returns.std() == 0:
            return 0.0
        # ffn calculates annualized sharpe ratio by default assuming daily data (rf=0)
        return float(daily_returns.calc_sharpe())


class SortinoRatio(PortfolioStatistic):
    @property
    def name(self) -> str:
        return "Sortino Ratio"

    def calculate(self, daily_returns: pd.Series, daily_values: pd.Series = None, **kwargs) -> float:
        if daily_returns.empty:
            return 0.0
        return float(daily_returns.calc_sortino())


class DailyMean(PortfolioStatistic):
    @property
    def name(self) -> str:
        return "Daily Mean"

    def calculate(self, daily_returns: pd.Series, daily_values: pd.Series = None, **kwargs) -> float:
        if daily_returns.empty:
            return 0.0
        return float(daily_returns.mean())


class AnnualizedVolatility(PortfolioStatistic):
    @property
    def name(self) -> str:
        return "Annualized Volatility"

    def calculate(self, daily_returns: pd.Series, daily_values: pd.Series = None, **kwargs) -> float:
        if daily_returns.empty:
            return 0.0
        return float(daily_returns.std() * np.sqrt(252))


class LastMonthDelta(PortfolioStatistic):
    @property
    def name(self) -> str:
        return "Last Month Delta"

    def calculate(self, daily_returns: pd.Series, daily_values: pd.Series = None, **kwargs) -> float:
        if daily_returns.empty:
            return 0.0
        # Last 30 days or calendar month
        last_date = daily_returns.index[-1]
        start_date = last_date - timedelta(days=30)
        recent_returns = daily_returns.loc[start_date:]
        if recent_returns.empty:
            return 0.0
        return float((1 + recent_returns).prod() - 1)

class CalmarRatio(PortfolioStatistic):
    @property
    def name(self) -> str:
        return "Calmar Ratio"

    def calculate(self, daily_returns: pd.Series, daily_values: pd.Series = None, **kwargs) -> float:
        if daily_returns.empty:
            return 0.0
        equity = (1 + daily_returns).cumprod()
        return float(equity.calc_calmar_ratio())


class Beta(PortfolioStatistic):
    @property
    def name(self) -> str:
        return "Beta"

    def calculate(self, daily_returns: pd.Series, daily_values: pd.Series = None, **kwargs) -> float:
        benchmark_returns = kwargs.get("benchmark_returns")
        if daily_returns.empty or benchmark_returns is None or benchmark_returns.empty:
            return 0.0
        
        # Align series by date
        aligned = pd.concat([daily_returns, benchmark_returns], axis=1, join="inner").dropna()
        if len(aligned) < 2:
            return 0.0
        
        cov = np.cov(aligned.iloc[:, 0], aligned.iloc[:, 1])[0, 1]
        var_b = np.var(aligned.iloc[:, 1], ddof=1)
        if var_b == 0:
            return 0.0
        return float(cov / var_b)

class Alpha(PortfolioStatistic):
    @property
    def name(self) -> str:
        return "Alpha (Annualized)"

    def calculate(self, daily_returns: pd.Series, daily_values: pd.Series = None, **kwargs) -> float:
        benchmark_returns = kwargs.get("benchmark_returns")
        if daily_returns.empty or benchmark_returns is None or benchmark_returns.empty:
            return 0.0
        
        aligned = pd.concat([daily_returns, benchmark_returns], axis=1, join="inner").dropna()
        if len(aligned) < 2:
            return 0.0
            
        cov = np.cov(aligned.iloc[:, 0], aligned.iloc[:, 1])[0, 1]
        var_b = np.var(aligned.iloc[:, 1], ddof=1)
        beta = float(cov / var_b) if var_b != 0 else 0.0
        
        port_eq = (1 + aligned.iloc[:, 0]).cumprod()
        bench_eq = (1 + aligned.iloc[:, 1]).cumprod()
        
        try:
            port_cagr = port_eq.calc_cagr()
            bench_cagr = bench_eq.calc_cagr()
        except Exception:
            return 0.0
            
        return float(port_cagr - beta * bench_cagr)
