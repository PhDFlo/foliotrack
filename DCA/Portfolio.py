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
        Initialize an empty portfolio of ETFs.
        """
        self.portfolio: list[dict[str, object]] = []
        self.total_to_invest = 0.


    def add_etf(self, etf: ETF, target_share: float = 1.0, amount_invested: float = 0.0):
        """
        Add an ETF to the portfolio with its portfolio share and invested amount.

        Args:
            etf (ETF): An instance of the ETF class to be added to the portfolio.
            target_share (float, optional): The share in the portfolio. Defaults to 1.0.
            amount_invested (float, optional): The amount of money already invested in this ETF. Defaults to 0.0.
        """
        self.portfolio.append({
            "etf": etf,
            "target_share": target_share,
            "amount_invested": amount_invested,
            "actual_share": 0.,
            "number_to_buy": 0., # Computed with equilibrium
            "final_share": 0. # Computed with equilibrium
        })
        print(f"ETF '{etf.name}' added to portfolio with share {target_share}.")


    def get_portfolio_info(self):
        """
        Get a summary of all ETFs in the portfolio.

        Returns:
            list: A list of dictionaries containing information about each ETF, its portfolio share, and amount invested.
        """
        return [
            {**item["etf"].get_info(), 
             "target_share": item["target_share"],
             "amount_invested": f"{item["amount_invested"]}€",
             "actual_share": item["actual_share"],
             "number_to_buy": item["number_to_buy"],
             "final_share": item["final_share"],
             }
            for item in self.portfolio
        ]


    def verify_target_share_sum(self):
        """
        Verify if the sum of the target portfolio shares is equal to 1.
        If not, print each ETF name with its associated share.
        Also print if the portfolio is complete or not.
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
        Compute the actual portfolio share of each ETF based on the amount invested.

        Returns:
            list: A list of dictionaries containing ETF info, its actual share in the portfolio, and updates the portfolio dicts with 'actual_share'.
        """
        
        # Verify if the Portfolio is complete
        if not self.verify_target_share_sum():
            raise Exception("Error, the portfolio is not complete.")
        
        total_invested = sum(item["amount_invested"] for item in self.portfolio)
        result = []
        for item in self.portfolio:
            if total_invested == 0:
                actual_share = 0.0
            else:
                actual_share = round(item["amount_invested"] / total_invested,2)
            item["actual_share"] = actual_share
    

    def solve_equilibrium(self, max_investment: float = 1000.0):
        """
        Compute the equilibrium portfolio based on target shares and maximum investment.

        Args:
            max_investment (float, optional): The maximum amount to invest in the portfolio. Defaults to 1000.0.
        Returns:
            None: Prints the number of each ETF to buy and their final shares in the portfolio.
        """
        
        # Number of ETF
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
        target_shares = np.array([item["target_share"] for item in self.portfolio])

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
        print("Final share of each ETF:")
        for i, item in enumerate(self.portfolio):
            item["final_share"] = round(final_shares[i],4)
            print(f"  {item['etf'].name}: {final_shares[i]:.4f}")
        
        print("")
        print(f"Total amount to invest: {self.total_to_invest:.2f}€")