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
        Initializes an empty portfolio for ETF management.
        """
        self.etfs: list[ETF] = []
        self.currency = currency
        self.staged_purchases = []  # List to store staged purchases

    def get_portfolio_info(self):
        """
        Returns a summary of all ETFs in the portfolio.
        """
        return [etf.get_info() for etf in self.etfs]

    def verify_target_share_sum(self):
        print()
        print("Verifying portfolio shares...")
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
        self.etfs.append(etf)
        print(f"ETF '{etf.name}' added to portfolio with share {etf.target_share} and number held {round(etf.number_held,4)}.")

    def buy_etf(self, etf_ticker: str, quantity: float, buy_price: float = None, fee: float = 0.0, date: str = None):
        for etf in self.etfs:
            if etf.ticker == etf_ticker:
                purchase = etf.buy(quantity, buy_price, fee, date)
                self.compute_actual_shares()
                self.staged_purchases.append(purchase)
                print(f"\nBought {quantity} units of '{etf_ticker}' on {purchase['date']}. New number held: {etf.number_held}. Number to buy reset.")
                return
        raise ValueError(f"ETF '{etf_ticker}' not found in the portfolio.")

    def compute_actual_shares(self):
        if not self.verify_target_share_sum():
            raise Exception("Error, the portfolio is not complete.")
        total_invested = sum(etf.amount_invested for etf in self.etfs)
        for etf in self.etfs:
            etf.compute_actual_share(total_invested)

    def update_etf_prices(self):
        for etf in self.etfs:
            etf.update_price_from_yfinance()

    @staticmethod
    def portfolio_from_csv(filepath):
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
