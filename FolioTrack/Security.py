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

    name: str  # Security name
    ticker: str = "DCAM"  # Security ticker symbol
    currency: str = "EUR"  # Security currency, either "EUR" or "USD"
    symbol: str = field(init=False)  # Symbol of the Security currency
    exchange_rate: float = 1.0  # Exchange rate to portfolio currency
    price_in_security_currency: float = 500.0  # Security price in its currency
    price_in_portfolio_currency: float = 500.0  # Security price in portfolio currency
    yearly_charge: float = 0.2  # Yearly charge in percentage
    number_held: float = 0.0  # Number of Security units held
    number_to_buy: float = 0.0  # Number of Security units to buy
    amount_to_invest: float = 0.0  # Amount to invest in this Security
    amount_invested: float = 0.0  # Total amount invested in this Security
    target_share: float = 1.0  # Target share of the Security in the portfolio
    actual_share: float = 0.0  # Actual share of the Security in the portfolio
    final_share: float = 0.0  # Final share of the Security after investment

    def __post_init__(self):
        """
        Initialize the Security instance with the given attributes.

        Computes the Security price in the portfolio currency and
        updates the amount invested in the Security.
        """
        self.price_in_portfolio_currency = round(
            self.price_in_security_currency * self.exchange_rate, 2
        )  # Security price in portfolio currency
        self.symbol = get_symbol(self.currency) or ""
        self.amount_invested = self.number_held * self.price_in_portfolio_currency

    def __repr__(self) -> str:
        """
        Return a string representation of the Security instance.
        """
        return (
            f"Security(name={self.name}, ticker={self.ticker}, currency={self.currency}, "
            f"price={self.price_in_security_currency}{self.symbol}, yearly_charge={self.yearly_charge})"
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
        buy_price: Optional[float] = None,
        fee: float = 0.0,
        date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Buy a specified quantity of this Security, updating number held and amount invested.
        """
        import datetime

        if date is None:
            date = datetime.datetime.now().strftime("%Y-%m-%d")
        if buy_price is None:
            buy_price = self.price_in_portfolio_currency
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
        Compute and update the actual share of this Security in the portfolio.
        """
        if total_invested == 0:
            self.actual_share = 0.0
        else:
            self.actual_share = round(self.amount_invested / total_invested, 2)

    def update_price_from_yfinance(self) -> None:
        """
        Update the Security price using yfinance based on its ticker, and update amount invested.
        """
        ticker = yf.Ticker(self.ticker)
        try:
            price_from_market = ticker.info.get("regularMarketPrice")
            if price_from_market is not None:
                self.price_in_security_currency = price_from_market
                self.price_in_portfolio_currency = (
                    self.price_in_security_currency * self.exchange_rate
                )

                self.amount_invested = round(
                    self.number_held * self.price_in_portfolio_currency, 2
                )
        except Exception as e:
            logging.error(f"Could not update price for {self.ticker}: {e}")

    def compute_price_in_portfolio_currency(self, portfolio_currency: str) -> None:
        """
        Compute and update the price of this Security in the specified portfolio currency.
        If the currency of this Security is different from the portfolio currency, it will
        fetch the exchange rate and update the price accordingly.
        If an error occurs while fetching the exchange rate, it will log the error.
        """
        if self.currency.lower() != portfolio_currency.lower():
            try:
                self.exchange_rate = float(
                    get_rate_between(self.currency.upper(), portfolio_currency.upper())
                )
                self.price_in_portfolio_currency = round(
                    float(self.price_in_security_currency * self.exchange_rate), 2
                )
            except Exception as e:
                logging.error(
                    f"Could not get exchange rate for {self.currency} to {portfolio_currency}: {e}"
                )

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
            exchange_rate=float(data.get("exchange_rate", 1.0)),
            price_in_security_currency=float(
                data.get("price_in_security_currency", 500.0)
            ),
            price_in_portfolio_currency=float(
                data.get("price_in_portfolio_currency", 500.0)
            ),
            yearly_charge=float(data.get("yearly_charge", 0.2)),
            number_held=float(data.get("number_held", 0.0)),
            number_to_buy=float(data.get("number_to_buy", 0.0)),
            amount_to_invest=float(data.get("amount_to_invest", 0.0)),
            amount_invested=float(data.get("amount_invested", 0.0)),
            target_share=float(data.get("target_share", 1.0)),
            actual_share=float(data.get("actual_share", 0.0)),
            final_share=float(data.get("final_share", 0.0)),
        )
