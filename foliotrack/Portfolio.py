import logging
import json
import csv
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from .Security import Security
from .Currency import get_symbol


@dataclass
class Portfolio:
    """
    Represents a portfolio containing multiple Securitys and a currency.
    """

    securities: List[Security] = field(
        default_factory=list
    )  # List of Securitys in the portfolio
    currency: str = "EUR"  # Portfolio currency
    symbol: str = field(init=False)  # Currency symbol
    staged_purchases: List[Dict[str, Any]] = field(
        default_factory=list
    )  # Securitys being bought

    def __post_init__(self):
        """
        Initialize the Portfolio instance by updating the currency symbol.

        Sets the `symbol` attribute to the symbol of the `currency` attribute.
        """
        self.symbol = get_symbol(self.currency) or ""

    def add_security(self, security: Security) -> None:
        """
        Adds a Security to the portfolio.

        Args:
            security (Security): Security instance to add to the portfolio.

        Logs a message indicating the Security has been added with its target share and number held.
        """
        self.securities.append(security)
        logging.info(
            f"Security '{security.name}' added to portfolio with share {security.target_share} and number held {round(security.number_held, 4)}."
        )

    def remove_security(self, ticker: str) -> None:
        """
        Removes a Security from the portfolio.

        Args:
            ticker (str): Ticker of the Security to remove from the portfolio.

        Logs a message indicating the Security has been removed.
        """
        self.securities = [
            security for security in self.securities if security.ticker != ticker
        ]

    def get_portfolio_info(self) -> List[Dict[str, Any]]:
        """
        Returns a list of dictionaries containing information about each Security in the portfolio.

        The list will contain dictionaries with the following keys:

        - name: str
        - ticker: str
        - currency: str
        - symbol: str
        - price_in_security_currency: float
        - price_in_portfolio_currency: float
        - yearly_charge: float
        - target_share: float
        - actual_share: float
        - final_share: float
        - number_held: float
        - number_to_buy: float
        - amount_to_invest: float
        - amount_invested: float

        :return: List of dictionaries containing Security information.
        :rtype: List[Dict[str, Any]]
        """
        return [security.get_info() for security in self.securities]

    def verify_target_share_sum(self) -> bool:
        """
        Verifies if the target shares of all Securities in the portfolio sum to 1.

        Logs a warning if the sum is not equal to 1 and returns False.
        Logs an info message if the sum is equal to 1 and returns True.

        :return: True if the target shares sum to 1, False otherwise
        :rtype: bool
        """
        total_share = sum(security.target_share for security in self.securities)
        if abs(total_share - 1.0) > 1e-6:
            logging.warning(f"Portfolio shares do not sum to 1. (Sum: {total_share})")
            return False
        logging.info("Portfolio shares sum equal to 1. Portfolio is complete.")
        return True

    def buy_security(
        self,
        security_ticker: str,
        quantity: float,
        buy_price: Optional[float] = None,
        fee: float = 0.0,
        date: Optional[str] = None,
    ) -> None:
        """
        Buys a specified quantity of a Security in the portfolio, updating number held and amount invested.

        Args:
            security_ticker (str): The ticker of the Security to buy.
            quantity (float): The quantity of the Security to buy.
            buy_price (Optional[float], optional): The price at which the Security is bought. Defaults to None.
            fee (float, optional): The fee associated with the purchase. Defaults to 0.0.
            date (Optional[str], optional): The date of the purchase. Defaults to None.

        Raises:
            ValueError: If the Security is not found in the portfolio.
        """
        for security in self.securities:
            if security.ticker == security_ticker:
                purchase = security.buy(quantity, buy_price, fee, date)
                self.compute_actual_shares()
                self.staged_purchases.append(purchase)
                logging.info(
                    f"Bought {quantity} units of '{security_ticker}' on {purchase['date']}. New number held: {security.number_held}."
                )
                return
        logging.error(f"Security '{security_ticker}' not found in the portfolio.")
        raise ValueError(f"Security '{security_ticker}' not found in the portfolio.")

    def compute_actual_shares(self) -> None:
        """
        Computes the actual share of each Security in the portfolio.
        It will raise an Exception if the portfolio is not complete.
        It first computes the total amount invested in the portfolio.
        Then it iterates over each Security in the portfolio, ensuring its price is in the portfolio currency,
        and computes its actual share based on the total invested.
        """
        if not self.verify_target_share_sum():
            raise Exception("Error, the portfolio is not complete.")
        total_invested = sum(security.amount_invested for security in self.securities)
        for security in self.securities:
            security.compute_price_in_portfolio_currency(
                self.currency
            )  # Ensure price is in portfolio currency
            security.compute_actual_share(total_invested)

    def update_security_prices(self) -> None:
        """
        Update the price of each Security in the portfolio using yfinance.
        """
        for security in self.securities:
            security.update_price_from_yfinance()

    def to_json(self, filepath: str) -> None:
        """
        Saves the portfolio to a JSON file.

        Args:
            filepath (str): Path to the JSON file to save the portfolio to.

        Raises:
            Exception: If an error occurs while saving the portfolio to JSON.
        """
        self.compute_actual_shares()  # Ensure shares are up to date
        try:
            with open(filepath, "w") as f:
                json.dump(
                    {
                        "currency": self.currency,
                        "securities": [
                            security.get_info() for security in self.securities
                        ],
                        "staged_purchases": self.staged_purchases,
                    },
                    f,
                    indent=4,
                )
            logging.info(f"Portfolio saved to {filepath}")
        except Exception as e:
            logging.error(f"Error saving portfolio to JSON: {e}")

    @classmethod
    def from_json(cls, filepath: str) -> "Portfolio":
        """
        Loads a Portfolio from a JSON file.

        Args:
            filepath (str): Path to the JSON file to load the portfolio from.

        Returns:
            Portfolio: The loaded Portfolio instance.

        Raises:
            Exception: If an error occurs while loading the portfolio from JSON.
        """
        try:
            with open(filepath, "r") as f:
                data = json.load(f)
            securities = [
                Security.from_json(security_data)
                for security_data in data["securities"]
            ]
            staged_purchases = data.get("staged_purchases", [])
            return cls(
                securities=securities,
                currency=data["currency"],
                staged_purchases=staged_purchases,
            )
        except Exception as e:
            logging.error(f"Error loading portfolio from JSON: {e}")
            return cls()

    def purchases_to_wealthfolio_csv(self, filepath: str) -> None:
        """
        Exports the staged purchases to a Wealthfolio-compatible CSV file.

        Args:
            filepath (str): Path to the CSV file to export the purchases to.

        Raises:
            Exception: If an error occurs while exporting the purchases to CSV.
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
        try:
            with open(filepath, mode="w", newline="", encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for purchase in self.staged_purchases:
                    currency = next(
                        (
                            security.currency
                            for security in self.securities
                            if security.ticker == purchase["ticker"]
                        ),
                        "",
                    )
                    amount = (
                        purchase["quantity"] * purchase["buy_price"] + purchase["fee"]
                    )
                    writer.writerow(
                        {
                            "date": purchase["date"],
                            "symbol": purchase["ticker"],
                            "quantity": purchase["quantity"],
                            "activityType": "Buy",
                            "unitPrice": purchase["buy_price"],
                            "currency": currency,
                            "fee": purchase["fee"],
                            "amount": amount,
                        }
                    )
            logging.info(f"Purchases exported to {filepath}")
        except Exception as e:
            logging.error(f"Error exporting purchases to Wealthfolio CSV: {e}")
