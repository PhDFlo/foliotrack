import numpy as np
import cvxpy as cp


class Equilibrate:
    @staticmethod
    def solve_equilibrium(
        portfolio,
        Investment_amount: float = 1000.0,
        Min_percent_to_invest: float = 0.99,
    ):
        """
        Solves for the optimal number of each ETF to buy to approach target shares,
        given a maximum investment. Updates the portfolio with the number to buy and
        final share for each ETF, and prints results.

        Args:
            portfolio: List of portfolio items (dicts with 'etf', 'amount_invested', 'target_share', etc.)
            Investment_amount (float, optional): Amount to invest. Defaults to 1000.0.
            Min_percent_to_invest (float, optional): Minimum percentage of the total investment to consider. Defaults to 0.99.

        Prints:
            - Optimization status
            - Number of each ETF to buy
            - Final share of each ETF
            - Total amount to invest
        """
        n = len(portfolio)
        if n == 0:
            raise ValueError("Portfolio is empty.")

        investments = cp.Variable(n, integer=True)
        price_matrix = np.diag([item["etf"].price for item in portfolio])
        invested_amounts = np.array([item["amount_invested"] for item in portfolio])
        target_shares = np.array([item["target_share"] for item in portfolio])

        constraints = [
            investments >= 0,
            cp.sum(price_matrix @ investments)
            >= Min_percent_to_invest * Investment_amount,
            cp.sum(price_matrix @ investments) <= Investment_amount,
        ]

        error = cp.norm(
            (invested_amounts + price_matrix @ investments)
            - cp.sum(invested_amounts + price_matrix @ investments) * target_shares,
            2,
        )

        objective = cp.Minimize(error)
        problem = cp.Problem(objective, constraints)
        problem.solve()

        print("")
        print("Optimisation status:", problem.status)

        if investments.value is None:
            raise RuntimeError("Optimization did not produce a solution.")
        etf_counts = np.round(investments.value).astype(int)
        print("")
        print("Number of each ETF to buy:")
        for i, item in enumerate(portfolio):
            item["number_to_buy"] = etf_counts[i]
            print(f"  {item['etf'].name}: {etf_counts[i]} units")

        final_invested = invested_amounts + price_matrix @ etf_counts
        total_invested = np.sum(final_invested)
        total_to_invest = np.sum(price_matrix @ etf_counts)

        if total_invested > 0:
            final_shares = final_invested / total_invested
        else:
            final_shares = np.zeros_like(final_invested)

        print("")
        print("Amount to spend and final share of each ETF:")
        for i, item in enumerate(portfolio):
            item["amount_to_invest"] = round(price_matrix[i, i] * etf_counts[i], 2)
            item["final_share"] = round(final_shares[i], 4)
            print(
                f"  {item['etf'].name}: {item['amount_to_invest']:.2f}{item['etf'].symbol}, Final share = {item['final_share']:.4f}"
            )

        print("")
        total_amounts = {}
        for i, item in enumerate(portfolio):
            symbol = item["etf"].symbol
            total_amounts.setdefault(symbol, 0)
            total_amounts[symbol] += item["amount_to_invest"]
        print("Total amount to invest:")
        for symbol, amount in total_amounts.items():
            print(f"  {amount:.2f}{symbol}")

        return etf_counts, total_to_invest, final_shares
