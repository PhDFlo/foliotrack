import bt
from .Portfolio import Portfolio


class Backtest:
    def run_backtest(self, portfolio: Portfolio, start_date, end_date):
        # Create a strategy based on the portfolio

        target_shares = self._get_list_target_shares(portfolio)
        print("Target shares:", target_shares)

        tickers = self._get_list_tickers(portfolio)
        print("Tickers:", tickers)

        strategy = bt.Strategy(
            "Portfolio Strategy",
            [
                bt.algos.RunMonthly(),
                bt.algos.SelectAll(),
                bt.algos.WeighEqually(),
                bt.algos.Rebalance(),
            ],
        )

        # Create a backtest
        # backtest = bt.Backtest(
        #    strategy, self.portfolio.get_price_data(start_date, end_date)
        # )

        # Run the backtest
        # result = bt.run(backtest)

        return  # result

    def _get_list_target_shares(self, portfolio: Portfolio):
        target_shares = []
        for ticker in portfolio.securities:
            target_shares.append(portfolio._get_share(ticker).target)

        return target_shares

    def _get_list_tickers(self, portfolio: Portfolio):
        tickers = []
        for ticker in portfolio.securities:
            tickers.append(ticker)

        return tickers


_BACKTEST = Backtest()

run_backtest = _BACKTEST.run_backtest
