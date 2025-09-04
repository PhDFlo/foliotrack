# This code is describing the portfolio class for the management system for ETFs (Exchange-Traded Funds).

from .ETF import ETF
import numpy as np
import cvxpy as cp
import csv
import datetime


class PortfolioETF:
    """
    A class to represent a portfolio of ETFs.

    Attributes:
        portfolio (list[tuple[ETF, float]]): A list of tuples (ETF instance, target_share).
    """

    def __init__(self, currency: str = "EUR"):
        """
        Initialize an empty portfolio for ETF management.

        Args:
            currency (str): The currency of the portfolio (default 'EUR').
        """
        self.etfs: list[ETF] = []
        self.currency = currency
        self.staged_purchases = []  # List to store staged purchases

    def get_portfolio_info(self):
        """
        Returns a summary of all ETFs in the portfolio as a list of dictionaries.

        Returns:
            list: List of dictionaries with ETF details and portfolio metrics.
        """
        return [etf.get_info() for etf in self.etfs]

    def verify_target_share_sum(self):
        """
        Checks if the sum of target shares for all ETFs equals 1.
        Prints details and completeness status.

        Returns:
            bool: True if sum equals 1, False otherwise.
        """
        print("\nVerifying portfolio shares...")
        total_share = sum(etf.target_share for etf in self.etfs)
        if abs(total_share - 1.0) > 1e-6:
            print("Portfolio shares do not sum to 1. Details:")
            for etf in self.etfs:
                print(f"  {etf.name}: {etf.target_share}")
            print(f"Portfolio is NOT complete. (Sum: {total_share})")
            return False
        else:
            print("Portfolio shares sum equal to 1. Portfolio is complete.")
            return True

    def add_new_etf(self, etf: ETF):
        """
        Adds an ETF to the portfolio.

        Args:
            etf (ETF): The ETF instance to add.
        """
        self.etfs.append(etf)
        print(f"ETF '{etf.name}' added to portfolio with share {etf.target_share} and number held {round(etf.number_held,4)}.")

    def buy_etf(self, etf_ticker: str, quantity: float, buy_price: float = None, fee: float = 0.0, date: str = None):
        """
        Buys a specified quantity of an ETF in the portfolio.

        Args:
            etf_ticker (str): The ticker of the ETF to buy.
            quantity (float): The number of units to buy.
            buy_price (float, optional): The price at which to buy the ETF. If None, uses current price.
            fee (float, optional): Transaction fee for the purchase. Defaults to 0.0.
            date (str, optional): Date of the purchase in yyyy-mm-dd format. Defaults to today's date.

        Raises:
            ValueError: If the ETF is not found in the portfolio.
        """
        for etf in self.etfs:
            if etf.ticker == etf_ticker:
                purchase = etf.buy(quantity, buy_price, fee, date)
                self.compute_actual_shares()
                self.staged_purchases.append(purchase)
                print(f"\nBought {quantity} units of '{etf_ticker}' on {purchase['date']}. New number held: {etf.number_held}. Number to buy reset.")
                return
        raise ValueError(f"ETF '{etf_ticker}' not found in the portfolio.")

    def compute_actual_shares(self):
        """
        Computes and updates the actual share of each ETF in the portfolio
        based on the amount invested. Requires the portfolio to be complete.

        Raises:
            Exception: If the portfolio target shares do not sum to 1.
        """
        if not self.verify_target_share_sum():
            raise Exception("Error, the portfolio is not complete.")
        total_invested = sum(etf.amount_invested for etf in self.etfs)
        for etf in self.etfs:
            etf.compute_actual_share(total_invested)

    def update_etf_prices(self):
        """
        Update prices for all ETFs in the portfolio using yfinance,
        and update the amount invested for each ETF based on the new price and number held.
        """
        for etf in self.etfs:
            etf.update_price_from_yfinance()

    @staticmethod
    def portfolio_from_csv(filepath):
        """
        Create a PortfolioETF instance from a CSV file.
        CSV columns: Name,Ticker,Currency,Price,Yearly Charge,Target Share,Amount Invested,Number Held

        Args:
            filepath (str): Path to the CSV file.

        Returns:
            PortfolioETF: The populated portfolio.
        """
        portfolio = PortfolioETF()
        with open(filepath, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                name = row.get("Name")
                ticker = row.get("Ticker")
                currency = row.get("Currency")
                price = float(row.get("Price", 0))
                yearly_charge = float(row.get("Yearly Charge", 0))
                target_share = float(row.get("Target Share", 0))
                number_held = float(row.get("Number Held", 0))
                from .ETF import ETF
                etf = ETF(
                    name=name,
                    ticker=ticker,
                    currency=currency,
                    price=price,
                    yearly_charge=yearly_charge,
                    target_share=target_share,
                    number_held=number_held,
                )
                portfolio.add_new_etf(etf)
        return portfolio

    def portfolio_to_csv(self, filepath):
        """
        Write the portfolio to a CSV file.
        Columns: Name,Ticker,Currency,Price,Yearly Charge,Target Share,Amount Invested,Number Held

        Args:
            filepath (str): Path to the CSV file.
        """
        with open(filepath, mode="w", newline="", encoding="utf-8") as csvfile:
            fieldnames = [
                "Name",
                "Ticker",
                "Currency",
                "Price",
                "Yearly Charge",
                "Target Share",
                "Amount Invested",
                "Number Held",
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for etf in self.etfs:
                writer.writerow(
                    {
                        "Name": etf.name,
                        "Ticker": etf.ticker,
                        "Currency": etf.currency,
                        "Price": etf.price,
                        "Yearly Charge": getattr(etf, "yearly_charge", ""),
                        "Target Share": etf.target_share,
                        "Amount Invested": etf.amount_invested,
                        "Number Held": etf.number_held,
                    }
                )

    def purchases_to_Wealthfolio_csv(self, filepath):
        """
        Write the staged purchases to a CSV file in Wealthfolio format:
        date, symbol, quantity, activityType, unitPrice, currency, fee, amount

        Args:
            filepath (str): Path to the output CSV file.
        """
        fieldnames = [
            "date",
            "symbol",
            "quantity",
            "activityType",
            "unitPrice",
            "currency",
            "fee",
            "amount",
        ]
        with open(filepath, mode="w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for purchase in self.staged_purchases:
                currency = None
                for etf in self.etfs:
                    if etf.ticker == purchase["ticker"]:
                        currency = etf.currency
                        break
                amount = purchase["quantity"] * purchase["buy_price"] + purchase["fee"]
                writer.writerow(
                    {
                        "date": purchase["date"],
                        "symbol": purchase["ticker"],
                        "quantity": purchase["quantity"],
                        "activityType": "Buy",
                        "unitPrice": purchase["buy_price"],
                        "currency": currency if currency else "",
                        "fee": purchase["fee"],
                        "amount": amount,
                    }
                )
