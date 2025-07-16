# This code is describing the portfolio class for the management system for ETFs (Exchange-Traded Funds).

from .ETF import ETF
import numpy as np
import cvxpy as cp

class PortfolioETF:
    """
    A class to represent a portfolio of ETFs.

    Attributes:
        portfolio (list[tuple[ETF, float]]): A list of tuples (ETF instance, portfolio_share).
    """

    def __init__(self):
        """
        Initialize an empty portfolio of ETFs.
        """
        self.portfolio: list[dict[str, object]] = []
        self.total_to_invest = 0.

    def add_etf(self, etf: ETF, portfolio_share: float = 1.0, amount_invested: float = 0.0):
        """
        Add an ETF to the portfolio with its portfolio share and invested amount.

        Args:
            etf (ETF): An instance of the ETF class to be added to the portfolio.
            portfolio_share (float, optional): The share in the portfolio. Defaults to 1.0.
            amount_invested (float, optional): The amount of money already invested in this ETF. Defaults to 0.0.
        """
        self.portfolio.append({
            "etf": etf,
            "portfolio_share": portfolio_share,
            "amount_invested": amount_invested
        })
        print(f"ETF '{etf.name}' added to portfolio with share {portfolio_share}.")

    def get_portfolio_info(self):
        """
        Get a summary of all ETFs in the portfolio.

        Returns:
            list: A list of dictionaries containing information about each ETF, its portfolio share, and amount invested.
        """
        return [
            {**item["etf"].get_info(), 
             "portfolio_share": item["portfolio_share"],
             "amount_invested": item["amount_invested"]}
            for item in self.portfolio
        ]

    def verify_shares_sum(self):
        """
        Verify if the sum of all portfolio shares is equal to 1.
        If not, print each ETF name with its associated share.
        Also print if the portfolio is complete or not.
        """
        print()
        print("Verifying portfolio shares...")
        total_share = sum(item["portfolio_share"] for item in self.portfolio)
        if abs(total_share - 1.0) > 1e-6:
            print("Portfolio shares do not sum to 1. Details:")
            for item in self.portfolio:
                print(f"  {item['etf'].name}: {item['portfolio_share']}")
            print(f"Portfolio is NOT complete. (Sum: {total_share})")
        else:
            print("Portfolio shares sum equal to 1. Portfolio is complete.")

    def compute_actual_shares(self):
        """
        Compute the actual portfolio share of each ETF based on the amount invested.

        Returns:
            list: A list of dictionaries containing ETF info, its actual share in the portfolio, and updates the portfolio dicts with 'actual_share'.
        """
        total_invested = sum(item["amount_invested"] for item in self.portfolio)
        result = []
        for item in self.portfolio:
            if total_invested == 0:
                actual_share = 0.0
            else:
                actual_share = round(item["amount_invested"] / total_invested,2)
            item["actual_share"] = actual_share
            info = {**item["etf"].get_info(),
                    "actual_share": actual_share,
                    "amount_invested": item["amount_invested"]}
            result.append(info)
        return result
    


    def solve_equilibrium(self, max_investment: float = 1000.0):
        """
        Compute the equilibrium portfolio based on target shares and maximum investment.

        Args:
            max_investment (float, optional): The maximum amount to invest in the portfolio. Defaults to 1000.0.
        Returns:
            None: The function prints the optimization status and optimal investments.
        """
        n = len(self.portfolio)
        if n == 0:
            raise ValueError("Portfolio is empty.")

        # Define variables
        investments = cp.Variable(n, integer=True)
        
        # Create price matrix
        price_matrix = np.diag([item["etf"].price for item in self.portfolio])
        
        # Create invested amounts array
        invested_amounts = np.array([item["amount_invested"] for item in self.portfolio])
        
        # Create target shares array
        target_shares = np.array([item["portfolio_share"] for item in self.portfolio])

        # Define constraints
        constraints = [
            investments >= 0,
            cp.sum(price_matrix@investments) <= max_investment,
        ]
        
        # Define the error function
        error = cp.norm((invested_amounts+price_matrix@investments)-cp.sum(invested_amounts+price_matrix@investments)*target_shares,2)
        
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
            print(f"  {item['etf'].name}: {etf_counts[i]}")
        
        # Calculate final invested amounts
        final_invested = invested_amounts + price_matrix @ etf_counts
        total_invested = np.sum(final_invested)
        total_to_invest = np.sum(price_matrix @ etf_counts)
        
        # Calculate final share of each ETF
        if total_invested > 0:
            final_shares = final_invested / total_invested
        else:
            final_shares = np.zeros_like(final_invested)
        
        print("")
        print("Final share of each ETF:")
        for i, item in enumerate(self.portfolio):
            print(f"  {item['etf'].name}: {final_shares[i]:.4f}")
        
        print("")
        print(f"Total amount to invest: {total_to_invest:.2f}€")


