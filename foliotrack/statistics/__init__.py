from .base import PortfolioStatistic
from .metrics import (
    TotalReturn,
    CAGR,
    MaxDrawdown,
    DailySharpe,
    AnnualizedSharpe,
    SortinoRatio,
    DailyMean,
    AnnualizedVolatility,
    LastMonthDelta,
    CalmarRatio,
    Alpha,
    Beta,
)

# Convenience list of default metrics
DEFAULT_METRICS = [
    TotalReturn(),
    CAGR(),
    MaxDrawdown(),
    DailySharpe(),
    AnnualizedSharpe(),
    SortinoRatio(),
    DailyMean(),
    AnnualizedVolatility(),
    LastMonthDelta(),
    CalmarRatio(),
    Alpha(),
    Beta(),
]

__all__ = [
    "PortfolioStatistic",
    "TotalReturn",
    "CAGR",
    "MaxDrawdown",
    "DailySharpe",
    "AnnualizedSharpe",
    "SortinoRatio",
    "DailyMean",
    "AnnualizedVolatility",
    "LastMonthDelta",
    "CalmarRatio",
    "Alpha",
    "Beta",
    "DEFAULT_METRICS",
]
