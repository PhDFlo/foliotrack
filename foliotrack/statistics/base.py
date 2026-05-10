import pandas as pd
from abc import ABC, abstractmethod


class PortfolioStatistic(ABC):
    """
    Abstract base class for all portfolio performance statistics.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the statistic"""
        pass

    @abstractmethod
    def calculate(
        self, daily_returns: pd.Series, daily_values: pd.Series = None, **kwargs
    ) -> float:
        """
        Calculates the statistic.

        Args:
            daily_returns (pd.Series): Time series of daily returns of the portfolio.
            daily_values (pd.Series, optional): Time series of daily values of the portfolio.

        Returns:
            float: The calculated statistic.
        """
        pass
