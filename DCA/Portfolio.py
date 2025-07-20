# This code is describing the portfolio class for the management system for ETFs (Exchange-Traded Funds).

from .ETF import ETF
import numpy as np
import cvxpy as cp


class PortfolioETF:
    """
    A class to represent a portfolio of ETFs.

    Attributes:
        portfolio (list[tuple[ETF, float]]): A list of tuples (ETF instance, target_share).
    """

    def __init__(self):
        """
        Initializes an empty portfolio for ETF management.
        """
        self.portfolio: list[dict[str, object]] = []
        self.total_to_invest = 0.0

    def add_etf(
        self, etf: ETF, target_share: float = 1.0, amount_invested: float = 0.0
    ):
        """
        Adds an ETF to the portfolio with its target share and invested amount.
        Also initializes fields for actual share, number to buy, and final share.

        Args:
            etf (ETF): The ETF instance to add.
            target_share (float, optional): Desired share of this ETF in the portfolio. Defaults to 1.0.
            amount_invested (float, optional): Amount already invested in this ETF. Defaults to 0.0.
        """
        self.portfolio.append(
            {
                "etf": etf,
                "target_share": target_share,
                "amount_invested": amount_invested,
                "actual_share": 0.0,
                "number_to_buy": 0.0,  # Computed with equilibrium
                "amount_to_invest": 0.0,  # Computed with equilibrium
                "final_share": 0.0,  # Computed with equilibrium
            }
        )
        print(f"ETF '{etf.name}' added to portfolio with share {target_share}.")

    def get_portfolio_info(self):
        """
        Returns a summary of all ETFs in the portfolio, including their info,
        target share, amount invested, actual share, number to buy, and final share.

        Returns:
            list: List of dictionaries with ETF details and portfolio metrics.
        """
        return [
            {
                **item["etf"].get_info(),
                "target_share": item["target_share"],
                "amount_invested": f"{item["amount_invested"]}€",
                "actual_share": item["actual_share"],
                "number_to_buy": item["number_to_buy"],
                "amount_to_invest": f"{item["amount_to_invest"]}€",
                "final_share": item["final_share"],
            }
            for item in self.portfolio
        ]

    def verify_target_share_sum(self):
        """
        Checks if the sum of target shares for all ETFs equals 1.
        Prints details and completeness status.

        Returns:
            bool: True if sum equals 1, False otherwise.
        """
        print()
        print("Verifying portfolio shares...")
        total_share = sum(item["target_share"] for item in self.portfolio)
        if abs(total_share - 1.0) > 1e-6:
            print("Portfolio shares do not sum to 1. Details:")
            for item in self.portfolio:
                print(f"  {item['etf'].name}: {item['target_share']}")
            print(f"Portfolio is NOT complete. (Sum: {total_share})")
            return False
        else:
            print("Portfolio shares sum equal to 1. Portfolio is complete.")
            return True

    def compute_actual_shares(self):
        """
        Computes and updates the actual share of each ETF in the portfolio
        based on the amount invested. Requires the portfolio to be complete.

        Raises:
            Exception: If the portfolio target shares do not sum to 1.
        """

        # Verify if the Portfolio is complete
        if not self.verify_target_share_sum():
            raise Exception("Error, the portfolio is not complete.")

        total_invested = sum(item["amount_invested"] for item in self.portfolio)
        result = []
        for item in self.portfolio:
            if total_invested == 0:
                actual_share = 0.0
            else:
                actual_share = round(item["amount_invested"] / total_invested, 2)
            item["actual_share"] = actual_share

    def solve_equilibrium(
        self, Investment_amount: float = 1000.0, Min_percent_to_invest: float = 0.99
    ):
        """
        Solves for the optimal number of each ETF to buy to approach target shares,
        given a maximum investment. Updates the portfolio with the number to buy and
        final share for each ETF, and prints results.

        Args:
            Investment_amount (float, optional): Amount to invest. Defaults to 1000.0.
            Min_percent_to_invest (float, optional): Minimum percentage of the total investment to consider. Defaults to 0.99.

        Prints:
            - Optimization status
            - Number of each ETF to buy
            - Final share of each ETF
            - Total amount to invest
        """

        # Number of ETF
        n = len(self.portfolio)
        if n == 0:
            raise ValueError("Portfolio is empty.")

        # Define variables
        investments = cp.Variable(n, integer=True)

        # Create price matrix
        price_matrix = np.diag([item["etf"].price for item in self.portfolio])

        # Create invested amounts array
        invested_amounts = np.array(
            [item["amount_invested"] for item in self.portfolio]
        )

        # Create target shares array
        target_shares = np.array([item["target_share"] for item in self.portfolio])

        # Define constraints
        constraints = [
            investments >= 0,
            cp.sum(price_matrix @ investments)
            >= Min_percent_to_invest * Investment_amount,
            cp.sum(price_matrix @ investments) <= Investment_amount,
        ]

        # Define the error function
        error = cp.norm(
            (invested_amounts + price_matrix @ investments)
            - cp.sum(invested_amounts + price_matrix @ investments) * target_shares,
            2,
        )

        # Form the optimization problem
        objective = cp.Minimize(error)

        # Solve the problem
        problem = cp.Problem(objective, constraints)
        problem.solve()

        print("")
        print("Optimisation status:", problem.status)

        # Calculate number of each ETF to buy (rounded to nearest integer)
        etf_counts = np.round(investments.value).astype(int)
        print("")
        print("Number of each ETF to buy:")
        for i, item in enumerate(self.portfolio):
            item["number_to_buy"] = etf_counts[i]
            print(f"  {item['etf'].name}: {etf_counts[i]}")

        # Calculate final invested amounts
        final_invested = invested_amounts + price_matrix @ etf_counts
        total_invested = np.sum(final_invested)
        self.total_to_invest = np.sum(price_matrix @ etf_counts)

        # Calculate final share of each ETF
        if total_invested > 0:
            final_shares = final_invested / total_invested
        else:
            final_shares = np.zeros_like(final_invested)

        print("")
        print("Amount to spend and final share of each ETF:")
        for i, item in enumerate(self.portfolio):
            item["amount_to_invest"] = price_matrix[i, i] * etf_counts[i]
            item["final_share"] = round(final_shares[i], 4)
            print(
                f"  {item['etf'].name}: {item["amount_to_invest"]:.2f}€, Final share = {item["final_share"]:.4f}"
            )

        print("")
        print(f"Total amount to invest: {self.total_to_invest:.2f}€")
