# This code is describing the portfolio class for the management system for ETFs (Exchange-Traded Funds).

from .ETF import ETF
import numpy as np

class PortfolioETF:
    """
    A class to represent a portfolio of ETFs.

    Attributes:
        etfs (list[tuple[ETF, float]]): A list of tuples (ETF instance, portfolio_share).
    """

    def __init__(self):
        """
        Initialize an empty portfolio of ETFs.
        """
        self.etfs: list[dict[str, object]] = []

    def add_etf(self, etf: ETF, portfolio_share: float = 1.0, amount_invested: float = 0.0):
        """
        Add an ETF to the portfolio with its portfolio share and invested amount.

        Args:
            etf (ETF): An instance of the ETF class to be added to the portfolio.
            portfolio_share (float, optional): The share in the portfolio. Defaults to 1.0.
            amount_invested (float, optional): The amount of money already invested in this ETF. Defaults to 0.0.
        """
        self.etfs.append({
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
            for item in self.etfs
        ]

    def verify_shares_sum(self):
        """
        Verify if the sum of all portfolio shares is equal to 1.
        If not, print each ETF name with its associated share.
        Also print if the portfolio is complete or not.
        """
        print()
        print("Verifying portfolio shares...")
        total_share = sum(item["portfolio_share"] for item in self.etfs)
        if abs(total_share - 1.0) > 1e-6:
            print("Portfolio shares do not sum to 1. Details:")
            for item in self.etfs:
                print(f"  {item['etf'].name}: {item['portfolio_share']}")
            print(f"Portfolio is NOT complete. (Sum: {total_share})")
        else:
            print("Portfolio shares sum equal to 1. Portfolio is complete.")

    def compute_actual_shares(self):
        """
        Compute the actual portfolio share of each ETF based on the amount invested.

        Returns:
            list: A list of dictionaries containing ETF info and its actual share in the portfolio.
        """
        total_invested = sum(item["amount_invested"] for item in self.etfs)
        if total_invested == 0:
            # Avoid division by zero, return zeros
            return [
                {**item["etf"].get_info(),
                 "actual_share": 0.0,
                 "amount_invested": item["amount_invested"]}
                for item in self.etfs
            ]
        return [
            {**item["etf"].get_info(),
             "actual_share": item["amount_invested"] / total_invested,
             "amount_invested": item["amount_invested"]}
            for item in self.etfs
        ]

    def generate_shares_matrix(self, exclude_etf: ETF = None):
        """
        Generate a square matrix of dimension n (number of ETFs in the portfolio minus one if exclude_etf is provided).
        The diagonal values are 1 - p, where p is the portfolio share of the ETF.
        All off-diagonal values are -p.
        The ETF given by exclude_etf is not included in the matrix.

        Args:
            exclude_etf (ETF, optional): ETF instance to exclude from the matrix. Defaults to None.

        Returns:
            np.ndarray: The generated matrix as a NumPy array.
        """
        filtered_etfs = [item for item in self.etfs if (exclude_etf is None or item["etf"] != exclude_etf)]
        n = len(filtered_etfs)
        matrix = np.zeros((n, n))
        for i in range(n):
            p = filtered_etfs[i]["portfolio_share"]
            for j in range(n):
                if i == j:
                    matrix[i, j] = 1 - p
                else:
                    matrix[i, j] = -p
        return matrix