import bt
import pandas as pd
import re
from foliotrack.domain.Portfolio import Portfolio

# Avoid circular import if type hinting MarketService by using TYPE_CHECKING or string
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from foliotrack.services.MarketService import MarketService


class BacktestService:
    def run_backtest(
        self,
        portfolio: Portfolio,
        market_service: "MarketService",
        start_date,
        end_date,
    ):
        """Run a backtest for the given portfolio.

        Args:
            portfolio (Portfolio): Portfolio containing securities and allocation info.
            market_service (MarketService): Service to fetch historical data.
            start_date (str or datetime): Start date for historical data (inclusive).
            end_date (str or datetime): End date for historical data (inclusive).

        Returns:
            bt.Result: Result object returned by bt.run containing backtest results.
        """
        # Prepare tickers
        tickers = self._get_list_tickers(portfolio)
        if not tickers:
            raise ValueError("Portfolio contains no securities to backtest.")

        # Fetch data using injected service
        historical_data = market_service.get_historical_data(
            tickers, start_date=start_date, end_date=end_date
        )

        # Get portfolio security target shares
        target_shares = self._get_list_target_shares(portfolio)
        if len(target_shares) != len(historical_data.columns):
            raise ValueError(
                "Number of target shares does not match number of tickers/data columns."
            )

        # bt.get often normalizes tickers (e.g., "AIR.PA" becomes "airpa").
        # To match them safely, we create a mapping from slugified ticker to target share.
        slug_to_share = {
            self._slugify(t): portfolio._get_share(t).target for t in tickers
        }

        # Build weights mapping columns from historical_data to their target shares
        weights_dict = {}
        for col in historical_data.columns:
            weights_dict[col] = slug_to_share.get(self._slugify(col), 0.0)

        # Build the weights DataFrame
        weights = pd.DataFrame(
            {
                col: [weights_dict[col]] * len(historical_data)
                for col in historical_data.columns
            },
            index=historical_data.index,
        )

        # Create a strategy
        strategy = bt.Strategy(
            portfolio.name,
            [
                bt.algos.RunMonthly(),
                bt.algos.SelectAll(),
                bt.algos.WeighTarget(weights),
                bt.algos.Rebalance(),
            ],
        )

        # Create a backtest
        backtest = bt.Backtest(strategy, historical_data)

        # Run the backtest
        result = bt.run(backtest)

        return result

    def _get_list_target_shares(self, portfolio: Portfolio):
        return [portfolio._get_share(ticker).target for ticker in portfolio.securities]

    def _get_list_tickers(self, portfolio: Portfolio):
        return list(portfolio.securities.keys())

    def _slugify(self, s):
        return re.sub(r"[^a-z0-9]", "", s.lower())
