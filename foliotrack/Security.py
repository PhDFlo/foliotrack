import yfinance as yf
import logging
from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any
from .Currency import get_symbol, get_rate_between


@dataclass
class Security:
    """
    A class to represent any security including Exchange-Traded Fund (ETF).
    """

    name: str = "Unnamed security"  # Name of the Security
    ticker: str = "DCAM"  # Security ticker symbol
    currency: str = "EUR"  # Currency of the Security
    symbol: str = field(init=False)  # Symbol of the Security currency
    exchange_rate: float = field(init=False)  # Exchange rate to portfolio currency
    price_in_security_currency: float = 500.0  # Security price in its currency
    price_in_portfolio_currency: float = field(
        init=False
    )  # Security price in portfolio currency
    quantity: float = 0.0  # Number of Security units held
    number_to_buy: float = field(init=False)  # Number of Security units to buy
    amount_to_invest: float = field(init=False)  # Amount to invest in this Security
    value: float = field(init=False)  # Total security value in portfolio currency
    fill: bool = True  # Boolean to fill attributes from yfinance

    def __post_init__(self):
        """
        Initialize the Security instance with the given attributes.

        Computes the Security price in the portfolio currency and
        updates the amount invested in the Security.
        """

        if self.fill:
            try:
                sec = yf.Ticker(self.ticker)

                self.name = sec.info.get("longName", "Unnamed Security")

                # If the security name is too short, only shortName is available
                if self.name == "Unnamed Security":
                    self.name = sec.info.get("shortName", "Unnamed Security")
                self.currency = sec.info.get("currency", "EUR")
            except Exception as e:
                logging.warning(f"Could not fetch security info for {self.ticker}: {e}")

        self.exchange_rate = 1.0
        self.number_to_buy = 0.0
        self.amount_to_invest = 0.0
        self.symbol = get_symbol(self.currency) or ""

        self.price_in_portfolio_currency = round(
            self.price_in_security_currency * self.exchange_rate, 2
        )  # Security price in portfolio currency
        self.value = self.quantity * self.price_in_portfolio_currency

    def __repr__(self) -> str:
        """
        Return a string representation of the Security instance.
        """
        return (
            f"Security(name={self.name}, ticker={self.ticker}, currency={self.currency}, "
            f"price={self.price_in_security_currency}{self.symbol})"
        )

    def get_info(self) -> Dict[str, Any]:
        """
        Get a dictionary containing the Security's information and all attributes.
        """
        info = asdict(self)
        info["symbol"] = self.symbol
        return info

    def buy(
        self,
        quantity: float,
        date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Buy a specified quantity of this Security, updating number held and amount invested.
        """
        import datetime

        if date is None:
            date = datetime.datetime.now().strftime("%Y-%m-%d")
        self.quantity += quantity
        self.value = quantity * self.price_in_portfolio_currency
        return {
            "ticker": self.ticker,
            "quantity": quantity,
            "date": date,
        }

    def sell(
        self,
        quantity: float,
        date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Sell a specified quantity of this Security, updating number held and amount invested.
        """
        import datetime

        if date is None:
            date = datetime.datetime.now().strftime("%Y-%m-%d")
        if quantity > self.quantity:
            raise ValueError(
                f"Cannot sell {quantity} units; only {self.quantity} available."
            )
        self.quantity -= quantity
        self.value = quantity * self.price_in_portfolio_currency
        return {
            "ticker": self.ticker,
            "quantity": -quantity,
            "date": date,
        }

    def update_security(self, portfolio_currency: str) -> None:
        """
        Update the Security price using yfinance based on its ticker,
        compute the exchange rate if needed, and update amount invested.
        """
        if self.fill:
            try:
                ticker = yf.Ticker(self.ticker)
                price_from_market = ticker.info.get("regularMarketPrice")
                if price_from_market is not None:
                    self.price_in_security_currency = price_from_market

                if self.currency.lower() != portfolio_currency.lower():
                    try:
                        self.exchange_rate = float(
                            get_rate_between(
                                self.currency.upper(), portfolio_currency.upper()
                            )
                        )
                    except Exception as e:
                        logging.error(
                            f"Could not get exchange rate for {self.currency} to {portfolio_currency}: {e}"
                        )

                self.price_in_portfolio_currency = round(
                    float(self.price_in_security_currency * self.exchange_rate), 2
                )

            except Exception as e:
                logging.error(f"Could not update price for {self.ticker}: {e}")

        self.value = round(self.quantity * self.price_in_portfolio_currency, 2)

    def to_json(self) -> Dict[str, Any]:
        """
        Serialize Security to a JSON-compatible dict.
        """
        return self.get_info()

    @staticmethod
    def from_json(data: Dict[str, Any]) -> "Security":
        """
        Deserialize Security from a JSON-compatible dict.
        """
        return Security(
            name=data.get("name", "Unnamed Security"),
            ticker=data.get("ticker", "DCAM"),
            currency=data.get("currency", "EUR"),
            price_in_security_currency=float(
                data.get("price_in_security_currency", 500.0)
            ),
            quantity=float(data.get("quantity", 0.0)),
            fill=bool(data.get("fill", True)),
        )
