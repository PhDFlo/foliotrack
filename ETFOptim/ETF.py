import yfinance as yf
import logging
from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any

@dataclass
class ETF:
    """
    A class to represent an Exchange-Traded Fund (ETF).
    """
    name: str                                    # ETF name
    ticker: str = "DCAM"                         # ETF ticker symbol
    currency: str = "EUR"                        # ETF currency, either "EUR" or "USD"
    symbol: str = field(init=False)              # Symbol of the ETF currency
    exchange_rate: float = 1.0                   # Exchange rate to portfolio currency
    price: float = 500.0                         # ETF price in its currency
    yearly_charge: float = 0.2                   # Yearly charge in percentage
    number_held: float = 0.0                     # Number of ETF units held
    number_to_buy: float = 0.0                   # Number of ETF units to buy
    amount_to_invest: float = 0.0                # Amount to invest in this ETF
    amount_invested: float = field(init=False)   # Total amount invested in this ETF
    target_share: float = 1.0                    # Target share of the ETF in the portfolio
    actual_share: float = 0.0                    # Actual share of the ETF in the portfolio
    final_share: float = 0.0                     # Final share of the ETF after investment

    def __post_init__(self):
        self.amount_invested = self.number_held * self.price
        if self.currency.lower() not in ["eur", "usd"]:
            logging.warning(f"Currency '{self.currency}' is not supported. Only EUR and USD are allowed.")
        if self.currency.lower() in ["eur", "€"]:
            self.symbol = "€"
        elif self.currency.lower() in ["usd", "$"]:
            self.symbol = "$"
        else:
            self.symbol = ""

    def __repr__(self) -> str:
        """
        Return a string representation of the ETF instance.
        """
        return (
            f"ETF(name={self.name}, ticker={self.ticker}, currency={self.currency}, "
            f"price={self.price}{self.symbol}, yearly_charge={self.yearly_charge})"
        )

    def get_info(self) -> Dict[str, Any]:
        """
        Get a dictionary containing the ETF's information and all attributes.
        """
        info = asdict(self)
        info["symbol"] = self.symbol
        return info

    def buy(self, quantity: float, buy_price: Optional[float] = None, fee: float = 0.0, date: Optional[str] = None) -> Dict[str, Any]:
        """
        Buy a specified quantity of this ETF, updating number held and amount invested.
        """
        import datetime
        if date is None:
            date = datetime.datetime.now().strftime("%Y-%m-%d")
        if buy_price is None:
            buy_price = self.price
        self.number_held += quantity
        self.amount_invested += quantity * buy_price
        return {
            "ticker": self.ticker,
            "quantity": quantity,
            "buy_price": buy_price,
            "fee": fee,
            "date": date,
        }

    def compute_actual_share(self, total_invested: float) -> None:
        """
        Compute and update the actual share of this ETF in the portfolio.
        """
        if total_invested == 0:
            self.actual_share = 0.0
        else:
            self.actual_share = round(self.amount_invested / total_invested, 2)

    def update_price_from_yfinance(self) -> None:
        """
        Update the ETF price using yfinance based on its ticker, and update amount invested.
        """
        ticker = yf.Ticker(self.ticker)
        try:
            price = ticker.info.get("regularMarketPrice")
            if price is not None:
                self.price = price
                self.amount_invested = self.number_held * self.price
        except Exception as e:
            logging.error(f"Could not update price for {self.ticker}: {e}")

    def to_json(self) -> Dict[str, Any]:
        """
        Serialize ETF to a JSON-compatible dict.
        """
        return self.get_info()

    @staticmethod
    def from_json(data: Dict[str, Any]) -> "ETF":
        """
        Deserialize ETF from a JSON-compatible dict.
        """
        return ETF(
            name=data["name"],
            ticker=data.get("ticker", "DCAM"),
            currency=data.get("currency", "EUR"),
            price=float(data.get("price", 500.0)),
            yearly_charge=float(data.get("yearly_charge", 0.2)),
            target_share=float(data.get("target_share", 1.0)),
            number_held=float(data.get("number_held", 0.0)),
        )