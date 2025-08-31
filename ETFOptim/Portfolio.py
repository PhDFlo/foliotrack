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

    def __init__(self):
        """
        Initializes an empty portfolio for ETF management.
        """
        self.portfolio: list[dict[str, object]] = []
        self.total_to_invest = 0.0
        self.staged_purchases = []  # List to store staged purchases
        
        
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
                "number_held": f"{item['number_held']}",
                "amount_invested": f"{item['amount_invested']}{item['etf'].symbol}",
                "actual_share": item["actual_share"],
                "number_to_buy": item["number_to_buy"],
                "amount_to_invest": f"{item['amount_to_invest']}{item['etf'].symbol}",
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
        

    def add_new_etf(self, etf: ETF, target_share: float = 1.0, number_held: float = 0.0):
        """
        Adds an ETF to the portfolio with its target share and number held.
        Also initializes fields for actual share, number to buy, and final share.

        Args:
            etf (ETF): The ETF instance to add.
            target_share (float, optional): Desired share of this ETF in the portfolio. Defaults to 1.0.
            number_held (float, optional): Number of ETF units currently held. Defaults to 0.0.
        """
        amount_invested = number_held * etf.price
        self.portfolio.append(
            {
                "etf": etf,
                "target_share": target_share,
                "number_held": number_held,
                "amount_invested": amount_invested,
                "actual_share": 0.0,
                "number_to_buy": 0.0,  # Computed with equilibrium
                "amount_to_invest": 0.0,  # Computed with equilibrium
                "final_share": 0.0,  # Computed with equilibrium
            }
        )
        print(
            f"ETF '{etf.name}' added to portfolio with share {target_share} and number held {round(number_held,4)}."
        )
    
    
    def buy_etf(self, etf_ticker: str, quantity: float, buy_price: float = None, fee: float = 0.0, date: str = None):
        """
        Buys a specified quantity of an ETF in the portfolio.

        Args:
            etf_ticker (str): The ticker of the ETF to buy.
            quantity (float): The number of units to buy.
            buy_price (float, optional): The price at which to buy the ETF. If None, uses current price. Defaults to None.
            fee (float, optional): Transaction fee for the purchase. Defaults to 0.0 (not used currently). 
            date (str, optional): Date of the purchase in yyyy-mm-dd format. Defaults to today's date (not used currently).
        Raises:
            ValueError: If the ETF is not found in the portfolio.
        """
        if date is None:
            date = datetime.datetime.now().strftime("%Y-%m-%d")
        for item in self.portfolio:
            if item["etf"].ticker == etf_ticker:
                item["number_held"] += quantity
                if buy_price is None: # Use current price if no buy price is provided
                    buy_price = item["etf"].price
                item["amount_invested"] = item["amount_invested"] + quantity * buy_price
                self.compute_actual_shares() # Update the actual shares
                item["number_to_buy"] = 0.0  # Reset number to buy
                # Add purchase to staged_purchases
                self.staged_purchases.append({
                    "ticker": etf_ticker,
                    "quantity": quantity,
                    "buy_price": buy_price,
                    "fee": fee,
                    "date": date
                })
                print(f"\nBought {quantity} units of '{etf_ticker}' on {date}. New number held: {item['number_held']}. Number to buy reset.")
                return
        raise ValueError(f"ETF '{etf_ticker}' not found in the portfolio.")

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

    def update_etf_prices(self):
        """
        Update prices for all ETFs in the portfolio using yfinance,
        and update the amount invested for each ETF based on the new price and number held.
        """
        for item in self.portfolio:
            etf = item["etf"]
            etf.update_price_from_yfinance()
            item["amount_invested"] = item["number_held"] * etf.price

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
                amount_invested = float(row.get("Amount Invested", 0))
                number_held = float(row.get("Number Held", 0))
                from .ETF import ETF

                etf = ETF(
                    name=name,
                    ticker=ticker,
                    currency=currency,
                    price=price,
                    yearly_charge=yearly_charge,
                )
                portfolio.add_new_etf(
                    etf, target_share=target_share, number_held=number_held
                )
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
            for item in self.portfolio:
                etf = item["etf"]
                writer.writerow(
                    {
                        "Name": etf.name,
                        "Ticker": etf.ticker,
                        "Currency": etf.currency,
                        "Price": etf.price,
                        "Yearly Charge": getattr(etf, "yearly_charge", ""),
                        "Target Share": item["target_share"],
                        "Amount Invested": item["amount_invested"],
                        "Number Held": item["number_held"],
                    }
                )
