from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any
import datetime
from foliotrack.utils.Currency import get_symbol


@dataclass
class Security:
    """
    A class to represent any security including Exchange-Traded Fund (ETF).
    Pure domain entity.
    """

    name: str = "Unnamed security"
    ticker: str = "DCAM"
    currency: str = "EUR"
    exchange_rate: float = 1.0
    price_in_security_currency: float = 500.0
    price_in_portfolio_currency: float = field(init=False)
    volume: float = 0.0
    volume_to_buy: float = 0.0
    amount_to_invest: float = 0.0
    value: float = field(init=False)
    fill: bool = True  # Metadata tag, not logic trigger anymore

    @property
    def symbol(self) -> str:
        """
        Get the currency symbol based on current currency code.
        """
        return get_symbol(self.currency) or ""

    def __post_init__(self):
        """
        Initialize derived attributes.
        """
        # Initialize price in portfolio currency based on default/initial exchange rate
        self.price_in_portfolio_currency = round(
            self.price_in_security_currency * self.exchange_rate, 2
        )
        self.value = round(self.volume * self.price_in_portfolio_currency, 2)

    def get_info(self) -> Dict[str, Any]:
        """
        Get a dictionary containing the Security's information and all attributes.
        """
        info = asdict(self)
        # asdict does not include properties
        info["symbol"] = self.symbol
        return info

    def buy(
        self,
        volume: float,
        date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Buy a specified volume of this Security, updating number held and amount invested.
        """
        if date is None:
            date = datetime.datetime.now().strftime("%Y-%m-%d")
        self.volume += volume
        self.value = round(self.volume * self.price_in_portfolio_currency, 2)
        self.volume_to_buy = (
            self.volume_to_buy - volume if self.volume_to_buy > volume else 0
        )
        return {
            "ticker": self.ticker,
            "volume": volume,
            "date": date,
        }

    def sell(
        self,
        volume: float,
        date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Sell a specified volume of this Security, updating number held and amount invested.
        """
        if date is None:
            date = datetime.datetime.now().strftime("%Y-%m-%d")
        if volume > self.volume:
            raise ValueError(
                f"Cannot sell {volume} units; only {self.volume} available."
            )
        self.volume -= volume
        self.value = round(self.volume * self.price_in_portfolio_currency, 2)
        self.volume_to_buy -= self.volume_to_buy - volume

        return {
            "ticker": self.ticker,
            "volume": -volume,
            "date": date,
        }
