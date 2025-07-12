# This code is describing the portfolio class for the management system for ETFs (Exchange-Traded Funds).

from .ETF import ETF

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