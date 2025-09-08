import logging
import json
import csv
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from .Security import Security


@dataclass
class Portfolio:
    """
    Represents a portfolio containing multiple Securitys and a currency.
    """

    securities: List[Security] = field(
        default_factory=list
    )  # List of Securitys in the portfolio
    currency: str = "EUR"  # Portfolio currency
    staged_purchases: List[Dict[str, Any]] = field(
        default_factory=list
    )  # Securitys being bought

    def add_security(self, security: Security) -> None:
        self.securities.append(security)
        logging.info(
            f"Security '{security.name}' added to portfolio with share {security.target_share} and number held {round(security.number_held, 4)}."
        )

    def remove_security(self, symbol: str) -> None:
        self.securities = [
            security for security in self.securities if security.symbol != symbol
        ]

    def get_portfolio_info(self) -> List[Dict[str, Any]]:
        return [security.get_info() for security in self.securities]

    def verify_target_share_sum(self) -> bool:
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
        if not self.verify_target_share_sum():
            raise Exception("Error, the portfolio is not complete.")
        total_invested = sum(security.amount_invested for security in self.securities)
        for security in self.securities:
            security.compute_price_in_portfolio_currency(
                self.currency
            )  # Ensure price is in portfolio currency
            security.compute_actual_share(total_invested)

    def update_security_prices(self) -> None:
        for security in self.securities:
            security.update_price_from_yfinance()

    def to_json(self, filepath: str) -> None:
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
