import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from dataclasses import dataclass, field
from .Security import Security
from .ShareInfo import ShareInfo
from foliotrack.utils.Currency import get_symbol


@dataclass
class Portfolio:
    """
    Represents a portfolio containing multiple Securitys and a currency.
    Pure domain entity.
    """

    name: str = "Unnamed portfolio"
    securities: Dict[str, Security] = field(default_factory=dict)
    shares: Dict[str, ShareInfo] = field(default_factory=dict)
    history: List[Dict[str, Any]] = field(default_factory=list)
    currency: str = "EUR"
    total_invested: float = field(init=False)

    @property
    def symbol(self) -> str:
        """
        Get the portfolio currency symbol based on current currency code.
        """
        return get_symbol(self.currency) or ""

    def __post_init__(self):
        self.total_invested = 0.0

        # Initialize shares entries for any pre-existing securities
        for ticker in self.securities:
            if ticker not in self.shares:
                self.shares[ticker] = ShareInfo()

    def buy_security(
        self,
        ticker,
        volume: float,
        currency: Optional[str] = None,
        price: Optional[float] = None,
        date: Optional[str] = None,
        fill: bool = True,
    ) -> None:
        """
        Buys a security. Does NOT handle auto-filling of name/price from external sources.
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        if ticker in self.securities:
            self.securities[ticker].buy(volume)
            logging.info(
                f"Bought {volume} units of existing security '{ticker}'. New number held: {round(self.securities[ticker].volume, 4)}."
            )
        else:
            # First time buying this security
            new_security = Security(
                ticker=ticker,
                currency=currency if currency is not None else self.currency,
                price_in_security_currency=price if price is not None else 0.0,
                volume=volume,
                fill=fill,
            )
            self.securities[ticker] = new_security
            logging.info(
                f"Security '{ticker}' added to portfolio with volume {round(volume, 4)}."
            )

        self.history.append(
            {
                "ticker": ticker,
                "volume": volume,
                "date": date,
            }
        )
        self.recalculate_shares()

    def sell_security(
        self,
        ticker: str,
        volume: float,
        date: Optional[str] = None,
    ) -> None:
        """
        Sells a volume of a security in the portfolio.
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        if ticker not in self.securities:
            raise ValueError(f"Security '{ticker}' not found in portfolio")

        security = self.securities[ticker]
        if security.volume < volume:
            raise ValueError(
                f"Insufficient volume to sell. Available: {security.volume}, Requested: {volume}"
            )
        elif security.volume == volume:
            del self.securities[ticker]
            self.shares.pop(ticker, None)
            logging.info(
                f"Sold all units of security '{ticker}'. Security removed from portfolio."
            )
        else:
            security.sell(volume)
            logging.info(
                f"Sold {volume} units of security '{ticker}'. New number held: {round(security.volume, 4)}."
            )

        self.history.append(
            {
                "ticker": ticker,
                "volume": -volume,
                "date": date,
            }
        )
        self.recalculate_shares()

    def recalculate_shares(self) -> None:
        """
        Compute total invested and actual shares based on current security prices.
        Does NOT fetch prices.
        """
        self.total_invested = sum(
            security.value for security in self.securities.values()
        )

        if self.total_invested == 0:
            for ticker in self.securities:
                self._get_share(ticker).actual = 0.0
        else:
            for ticker, security in self.securities.items():
                self._get_share(ticker).actual = round(
                    security.value / self.total_invested, 4
                )

    def set_target_share(self, ticker: str, share: float) -> None:
        if ticker not in self.securities:
            raise ValueError(f"Security '{ticker}' not found in portfolio")
        self._get_share(ticker).target = share

    def _get_share(self, ticker: str) -> ShareInfo:
        if ticker not in self.shares:
            self.shares[ticker] = ShareInfo()
        return self.shares[ticker]

    def get_portfolio_info(self) -> List[Dict[str, Any]]:
        info_list = []
        for ticker, security in self.securities.items():
            info = security.get_info()
            share_info = self._get_share(ticker)
            info["target_share"] = share_info.target
            info["actual_share"] = share_info.actual
            info["final_share"] = share_info.final
            info_list.append(info)
        return info_list
