import logging
import json
import csv
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from .ETF import ETF

@dataclass
class Portfolio:
    """
    Represents a portfolio containing multiple ETFs and a currency.
    """
    etfs: List[ETF] = field(default_factory=list)
    currency: str = "EUR"
    staged_purchases: List[Dict[str, Any]] = field(default_factory=list)

    def add_etf(self, etf: ETF) -> None:
        self.etfs.append(etf)
        logging.info(f"ETF '{etf.name}' added to portfolio with share {etf.target_share} and number held {round(etf.number_held, 4)}.")

    def remove_etf(self, symbol: str) -> None:
        self.etfs = [etf for etf in self.etfs if etf.symbol != symbol]

    def get_portfolio_info(self) -> List[Dict[str, Any]]:
        return [etf.get_info() for etf in self.etfs]

    def verify_target_share_sum(self) -> bool:
        total_share = sum(etf.target_share for etf in self.etfs)
        if abs(total_share - 1.0) > 1e-6:
            logging.warning(f"Portfolio shares do not sum to 1. (Sum: {total_share})")
            return False
        logging.info("Portfolio shares sum equal to 1. Portfolio is complete.")
        return True

    def buy_etf(self, etf_ticker: str, quantity: float, buy_price: Optional[float] = None, fee: float = 0.0, date: Optional[str] = None) -> None:
        for etf in self.etfs:
            if etf.ticker == etf_ticker:
                purchase = etf.buy(quantity, buy_price, fee, date)
                self.compute_actual_shares()
                self.staged_purchases.append(purchase)
                logging.info(f"Bought {quantity} units of '{etf_ticker}' on {purchase['date']}. New number held: {etf.number_held}.")
                return
        logging.error(f"ETF '{etf_ticker}' not found in the portfolio.")
        raise ValueError(f"ETF '{etf_ticker}' not found in the portfolio.")

    def compute_actual_shares(self) -> None:
        if not self.verify_target_share_sum():
            raise Exception("Error, the portfolio is not complete.")
        total_invested = sum(etf.amount_invested for etf in self.etfs)
        for etf in self.etfs:
            etf.compute_actual_share(total_invested)

    def update_etf_prices(self) -> None:
        for etf in self.etfs:
            etf.update_price_from_yfinance()

    def to_json(self, filepath: str) -> None:
        try:
            with open(filepath, 'w') as f:
                json.dump({
                    "currency": self.currency,
                    "etfs": [etf.get_info() for etf in self.etfs],
                    "staged_purchases": self.staged_purchases
                }, f, indent=4)
            logging.info(f"Portfolio saved to {filepath}")
        except Exception as e:
            logging.error(f"Error saving portfolio to JSON: {e}")

    @classmethod
    def from_json(cls, filepath: str) -> 'Portfolio':
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            etfs = [ETF.from_json(etf_data) for etf_data in data["etfs"]]
            staged_purchases = data.get("staged_purchases", [])
            return cls(etfs=etfs, currency=data["currency"], staged_purchases=staged_purchases)
        except Exception as e:
            logging.error(f"Error loading portfolio from JSON: {e}")
            return cls()

    def purchases_to_wealthfolio_csv(self, filepath: str) -> None:
        fieldnames = [
            "date", "symbol", "quantity", "activityType", "unitPrice", "currency", "fee", "amount"
        ]
        try:
            with open(filepath, mode="w", newline="", encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for purchase in self.staged_purchases:
                    currency = next((etf.currency for etf in self.etfs if etf.ticker == purchase["ticker"]), "")
                    amount = purchase["quantity"] * purchase["buy_price"] + purchase["fee"]
                    writer.writerow({
                        "date": purchase["date"],
                        "symbol": purchase["ticker"],
                        "quantity": purchase["quantity"],
                        "activityType": "Buy",
                        "unitPrice": purchase["buy_price"],
                        "currency": currency,
                        "fee": purchase["fee"],
                        "amount": amount,
                    })
            logging.info(f"Purchases exported to {filepath}")
        except Exception as e:
            logging.error(f"Error exporting purchases to Wealthfolio CSV: {e}")