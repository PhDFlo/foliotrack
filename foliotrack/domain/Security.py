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
    symbol: str = field(init=False)
    exchange_rate: float = 1.0
    price_in_security_currency: float = 500.0
    price_in_portfolio_currency: float = field(init=False)
    volume: float = 0.0
    volume_to_buy: float = 0.0
    amount_to_invest: float = 0.0
    value: float = field(init=False)
    fill: bool = True  # Metadata tag, not logic trigger anymore

    def __post_init__(self):
        """
        Initialize derived attributes.
        """
        self.symbol = get_symbol(self.currency) or ""
        # Initialize price in portfolio currency based on default/initial exchange rate
        self.price_in_portfolio_currency = round(
            self.price_in_security_currency * self.exchange_rate, 2
        )
        self.value = self.volume * self.price_in_portfolio_currency

    def get_info(self) -> Dict[str, Any]:
        """
        Get a dictionary containing the Security's information and all attributes.
        """
        info = asdict(self)
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
        self.value = self.volume * self.price_in_portfolio_currency
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
        self.value = self.volume * self.price_in_portfolio_currency
        # Logic for volume_to_buy update on sell?
        # Original: self.volume_to_buy -= self.volume_to_buy - volume (Evaluates to volume?)
        # Original code: self.volume_to_buy -= self.volume_to_buy - volume
        # => self.volume_to_buy = self.volume_to_buy - (self.volume_to_buy - volume) = volume
        # That looks weird in original code, but preserving logic for now or fixing if obvious bug.
        # Actually it looks like it sets volume_to_buy = volume ?
        # Let's keep it simple: usually selling doesn't affect 'to buy' unless we are undoing a planned buy.
        # But 'volume_to_buy' is populated by Equilibrate.
        # I'll preserve original behavior exactly for now.
        self.volume_to_buy -= self.volume_to_buy - volume

        return {
            "ticker": self.ticker,
            "volume": -volume,
            "date": date,
        }
