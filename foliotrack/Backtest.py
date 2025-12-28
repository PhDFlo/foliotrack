import bt
import pandas as pd
from .Portfolio import Portfolio


class Backtest:
    def run_backtest(self, portfolio: Portfolio, start_date, end_date):
        """Run a backtest for the given portfolio.

        Args:
            portfolio (Portfolio): Portfolio containing securities and allocation info.
            start_date (str or datetime): Start date for historical data (inclusive).
            end_date (str or datetime): End date for historical data (inclusive).

        Returns:
            bt.Result: Result object returned by bt.run containing backtest results.
        """
        # Prepare tickers
        tickers = self._get_list_tickers(portfolio)
        if not tickers:
            raise ValueError("Portfolio contains no securities to backtest.")

        # Data fetching
        historical_data = bt.get(tickers, start=start_date, end=end_date)

        # Get portfolio security target shares
        target_shares = self._get_list_target_shares(portfolio)
        if len(target_shares) != len(historical_data.columns):
            raise ValueError(
                "Number of target shares does not match number of tickers/data columns."
            )

        # Build a DataFrame where each column is a constant series equal to the target share
        weights = pd.DataFrame(
            {
                col: weight
                for col, weight in zip(historical_data.columns, target_shares)
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
        """Return the list of target share (weight) values for the portfolio's securities.

        Args:
            portfolio (Portfolio): Portfolio from which to extract target shares.

        Returns:
            List[float]: Target shares in the same order as portfolio.securities.
        """
        return [portfolio._get_share(ticker).target for ticker in portfolio.securities]

    def _get_list_tickers(self, portfolio: Portfolio):
        """Return a list of ticker identifiers for the portfolio.

        Args:
            portfolio (Portfolio): Portfolio whose security tickers are returned.

        Returns:
            List[str]: Ticker symbols in the same order as portfolio.securities.
        """
        return [ticker for ticker in portfolio.securities]


_BACKTEST = Backtest()

run_backtest = _BACKTEST.run_backtest
