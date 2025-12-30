import bt
import pandas as pd
from foliotrack.domain.Portfolio import Portfolio


class BacktestService:
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

        # Data fetching (bt handles its own fetching, usually from Yahoo Finance)
        # In a stricter system, we might inject data here.
        historical_data = bt.get(tickers, start=start_date, end=end_date)

        # Get portfolio security target shares
        target_shares = self._get_list_target_shares(portfolio)

        # Validation checks on data alignment
        # (This logic assumes tickers in portfolio match columns in data)
        # bt.get returns columns in sorted order or specific order?
        # Usually bt.get(tickers) returns DataFrame with columns=tickers.
        # But if we rely on order, we must be careful.
        # Original code used zip(historical_data.columns, target_shares) assuming alignment.
        # Assuming original code worked, but columns are usually sorted alphabetically by bt?
        # Let's verify or trust original Logic.
        # bt.get returns data for passed tickers. ORDER MATTERS for zip.
        # Original code:
        # tickers derived from portfolio.securities (iteration order)
        # target_shares derived from portfolio.securities (iteration order)
        # historical_data columns might be sorted by bt?
        # If bt sorts columns, and portfolio isn't sorted, we have a Mismatch Bug in original code?
        # I should probably fix this by matching columns to tickers explicitly.

        # Safe implementation:
        weights_dict = {}
        for ticker in tickers:
            share = portfolio._get_share(ticker).target
            if ticker in historical_data.columns:
                weights_dict[ticker] = share

        # If any ticker failed to load data, we might need to handle it.
        # But constructing weights dataframe:
        weights = pd.DataFrame(
            {col: weights_dict.get(col, 0.0) for col in historical_data.columns},
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
