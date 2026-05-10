import pandas as pd
import numpy as np
import ffn  # noqa: F401
from datetime import timedelta

from .base import PortfolioStatistic


class TotalReturn(PortfolioStatistic):
    @property
    def name(self) -> str:
        return "Total Return"

    def calculate(
        self, daily_returns: pd.Series, daily_values: pd.Series = None, **kwargs
    ) -> float:
        """
        Calculates the cumulative return over the entire period.
        Formula: (1 + r_1) * (1 + r_2) * ... * (1 + r_n) - 1.
        """
        if daily_returns.empty:
            return 0.0
        return float((1 + daily_returns).prod() - 1)


class CAGR(PortfolioStatistic):
    @property
    def name(self) -> str:
        return "CAGR"

    def calculate(
        self, daily_returns: pd.Series, daily_values: pd.Series = None, **kwargs
    ) -> float:
        """
        Calculates the Compound Annual Growth Rate (CAGR).
        Uses ffn to calculate the geometric average annual return from the equity curve.
        """
        if len(daily_returns) < 2:
            return 0.0
        # Create equity curve to use ffn
        equity = (1 + daily_returns).cumprod()
        # ffn's calc_cagr requires a pandas Series with DatetimeIndex
        return float(equity.calc_cagr())


class BenchmarkCAGR(PortfolioStatistic):
    @property
    def name(self) -> str:
        return "Benchmark CAGR"

    def calculate(
        self, daily_returns: pd.Series, daily_values: pd.Series = None, **kwargs
    ) -> float:
        """
        Calculates the Compound Annual Growth Rate (CAGR) of the benchmark.
        Formula: Geometric average annual return of the benchmark, aligned to the portfolio's dates.
        """
        benchmark_returns = kwargs.get("benchmark_returns")
        if daily_returns.empty or benchmark_returns is None or benchmark_returns.empty:
            return 0.0

        # Align series by date to match the portfolio's period
        aligned = pd.concat(
            [daily_returns, benchmark_returns], axis=1, join="inner"
        ).dropna()
        if len(aligned) < 2:
            return 0.0

        bench_eq = (1 + aligned.iloc[:, 1]).cumprod()

        try:
            return float(bench_eq.calc_cagr())
        except Exception:
            return 0.0


class MaxDrawdown(PortfolioStatistic):
    @property
    def name(self) -> str:
        return "Max Drawdown"

    def calculate(
        self, daily_returns: pd.Series, daily_values: pd.Series = None, **kwargs
    ) -> float:
        """
        Calculates the maximum historical drawdown (peak-to-trough).
        Uses ffn to measure the largest drop experienced by the portfolio.
        """
        if daily_returns.empty:
            return 0.0
        equity = (1 + daily_returns).cumprod()
        return float(equity.calc_max_drawdown())


class DailySharpe(PortfolioStatistic):
    @property
    def name(self) -> str:
        return "Daily Sharpe Ratio"

    def calculate(
        self, daily_returns: pd.Series, daily_values: pd.Series = None, **kwargs
    ) -> float:
        """
        Calculates the Sharpe Ratio on a daily basis.
        Formula: Mean(Returns) / Standard_Deviation(Returns).
        The risk-free rate is assumed to be 0 for simplicity.
        """
        if daily_returns.empty or daily_returns.std() == 0:
            return 0.0
        # Risk free rate assumed 0 for simplicity
        return float(daily_returns.mean() / daily_returns.std())


class AnnualizedSharpe(PortfolioStatistic):
    @property
    def name(self) -> str:
        return "Annualized Sharpe Ratio"

    def calculate(
        self, daily_returns: pd.Series, daily_values: pd.Series = None, **kwargs
    ) -> float:
        """
        Calculates the annualized Sharpe Ratio.
        Uses ffn to extrapolate the daily Sharpe over a year (assuming 252 trading days).
        The risk-free rate is assumed to be 0.
        """
        if daily_returns.empty or daily_returns.std() == 0:
            return 0.0
        # ffn calculates annualized sharpe ratio by default assuming daily data (rf=0)
        return float(daily_returns.calc_sharpe())


class BenchmarkAnnualizedSharpe(PortfolioStatistic):
    @property
    def name(self) -> str:
        return "Benchmark Annualized Sharpe Ratio"

    def calculate(
        self, daily_returns: pd.Series, daily_values: pd.Series = None, **kwargs
    ) -> float:
        """
        Calculates the annualized Sharpe Ratio of the benchmark.
        Aligned to the portfolio's dates.
        The risk-free rate is assumed to be 0.
        """
        benchmark_returns = kwargs.get("benchmark_returns")
        if daily_returns.empty or benchmark_returns is None or benchmark_returns.empty:
            return 0.0

        aligned = pd.concat(
            [daily_returns, benchmark_returns], axis=1, join="inner"
        ).dropna()
        if len(aligned) < 2 or aligned.iloc[:, 1].std() == 0:
            return 0.0

        return float(aligned.iloc[:, 1].calc_sharpe())


class SortinoRatio(PortfolioStatistic):
    @property
    def name(self) -> str:
        return "Sortino Ratio"

    def calculate(
        self, daily_returns: pd.Series, daily_values: pd.Series = None, **kwargs
    ) -> float:
        """
        Calculates the Sortino Ratio.
        Uses ffn. Similar to Sharpe, but only penalizes downside volatility (negative returns).
        """
        if daily_returns.empty:
            return 0.0
        return float(daily_returns.calc_sortino())


class DailyMean(PortfolioStatistic):
    @property
    def name(self) -> str:
        return "Daily Mean"

    def calculate(
        self, daily_returns: pd.Series, daily_values: pd.Series = None, **kwargs
    ) -> float:
        """
        Calculates the simple arithmetic mean of the daily returns.
        """
        if daily_returns.empty:
            return 0.0
        return float(daily_returns.mean())


class AnnualizedVolatility(PortfolioStatistic):
    @property
    def name(self) -> str:
        return "Annualized Volatility"

    def calculate(
        self, daily_returns: pd.Series, daily_values: pd.Series = None, **kwargs
    ) -> float:
        """
        Calculates the annualized volatility (standard deviation).
        Formula: Standard_Deviation(Daily Returns) * Square_Root(252 days).
        """
        if daily_returns.empty:
            return 0.0
        return float(daily_returns.std() * np.sqrt(252))


class BenchmarkAnnualizedVolatility(PortfolioStatistic):
    @property
    def name(self) -> str:
        return "Benchmark Annualized Volatility"

    def calculate(
        self, daily_returns: pd.Series, daily_values: pd.Series = None, **kwargs
    ) -> float:
        """
        Calculates the annualized volatility (standard deviation) of the benchmark.
        Formula: Standard_Deviation(Benchmark Returns) * Square_Root(252 days).
        Aligned to the portfolio's dates.
        """
        benchmark_returns = kwargs.get("benchmark_returns")
        if daily_returns.empty or benchmark_returns is None or benchmark_returns.empty:
            return 0.0

        aligned = pd.concat(
            [daily_returns, benchmark_returns], axis=1, join="inner"
        ).dropna()
        if len(aligned) < 2:
            return 0.0

        return float(aligned.iloc[:, 1].std() * np.sqrt(252))


class LastMonthDelta(PortfolioStatistic):
    @property
    def name(self) -> str:
        return "Last Month Delta"

    def calculate(
        self, daily_returns: pd.Series, daily_values: pd.Series = None, **kwargs
    ) -> float:
        """
        Calculates the absolute performance of the portfolio over the last 30 calendar days.
        Formula: Cumulative product of daily returns over this period.
        """
        if daily_returns.empty:
            return 0.0
        # Last 30 days or calendar month
        last_date = daily_returns.index[-1]
        start_date = last_date - timedelta(days=30)
        recent_returns = daily_returns.loc[start_date:]
        if recent_returns.empty:
            return 0.0
        return float((1 + recent_returns).prod() - 1)


class OneYearReturn(PortfolioStatistic):
    @property
    def name(self) -> str:
        return "1-Year Return"

    def calculate(
        self, daily_returns: pd.Series, daily_values: pd.Series = None, **kwargs
    ) -> float:
        """
        Calculates the absolute performance of the portfolio over the last 365 days.
        Formula: Cumulative product of daily returns over this period.
        """
        if daily_returns.empty:
            return 0.0
        last_date = daily_returns.index[-1]
        start_date = last_date - timedelta(days=365)
        recent_returns = daily_returns.loc[start_date:]
        if recent_returns.empty:
            return 0.0
        return float((1 + recent_returns).prod() - 1)


class YTDReturn(PortfolioStatistic):
    @property
    def name(self) -> str:
        return "YTD Return"

    def calculate(
        self, daily_returns: pd.Series, daily_values: pd.Series = None, **kwargs
    ) -> float:
        """
        Calculates the Year-To-Date (YTD) return of the portfolio.
        Formula: Cumulative product of daily returns from the beginning of the current year.
        """
        if daily_returns.empty:
            return 0.0
        last_year_str = str(daily_returns.index[-1].year)
        recent_returns = daily_returns.loc[last_year_str:]
        if recent_returns.empty:
            return 0.0
        return float((1 + recent_returns).prod() - 1)


class CalmarRatio(PortfolioStatistic):
    @property
    def name(self) -> str:
        return "Calmar Ratio"

    def calculate(
        self, daily_returns: pd.Series, daily_values: pd.Series = None, **kwargs
    ) -> float:
        """
        Calculates the Calmar Ratio.
        Uses ffn. The ratio between the annualized return (CAGR) and the maximum drawdown.
        """
        if daily_returns.empty:
            return 0.0
        equity = (1 + daily_returns).cumprod()
        return float(equity.calc_calmar_ratio())


class Beta(PortfolioStatistic):
    @property
    def name(self) -> str:
        return "Beta"

    def calculate(
        self, daily_returns: pd.Series, daily_values: pd.Series = None, **kwargs
    ) -> float:
        """
        Calculates Beta, measuring the sensitivity of the portfolio relative to a benchmark.
        Formula: Covariance(Portfolio, Benchmark) / Variance(Benchmark).
        """
        benchmark_returns = kwargs.get("benchmark_returns")
        if daily_returns.empty or benchmark_returns is None or benchmark_returns.empty:
            return 0.0

        # Align series by date
        aligned = pd.concat(
            [daily_returns, benchmark_returns], axis=1, join="inner"
        ).dropna()
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

    def calculate(
        self, daily_returns: pd.Series, daily_values: pd.Series = None, **kwargs
    ) -> float:
        """
        Calculates annualized Alpha.
        Measures the outperformance relative to the risk taken (Beta).
        Formula: Portfolio_CAGR - (Beta * Benchmark_CAGR).
        """
        benchmark_returns = kwargs.get("benchmark_returns")
        if daily_returns.empty or benchmark_returns is None or benchmark_returns.empty:
            return 0.0

        aligned = pd.concat(
            [daily_returns, benchmark_returns], axis=1, join="inner"
        ).dropna()
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
