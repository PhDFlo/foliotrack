import logging
import json
from typing import List, Optional, Dict, Any
from datetime import datetime
from dataclasses import dataclass, field
from .Security import Security
from .Currency import get_symbol


@dataclass
class ShareInfo:
    """Represents share information for a security in the portfolio"""

    target: float = 0.0
    actual: float = 0.0
    final: float = 0.0

    def to_dict(self) -> Dict[str, float]:
        """Serialize ShareInfo to a plain dict."""
        return {
            "target": float(self.target),
            "actual": float(self.actual),
            "final": float(self.final),
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "ShareInfo":
        """Create ShareInfo from a dict, tolerates missing keys."""
        si = ShareInfo()
        if not isinstance(d, dict):
            return si
        try:
            si.target = float(d.get("target", si.target))
            si.actual = float(d.get("actual", si.actual))
            si.final = float(d.get("final", si.final))
        except Exception:
            # Keep defaults if conversion fails
            pass
        return si


@dataclass
class Portfolio:
    """
    Represents a portfolio containing multiple Securitys and a currency.
    """

    name: str = "Unnamed portfolio"  # Name of the Portfolio
    securities: Dict[str, Security] = field(
        default_factory=dict
    )  # Maps ticker to Security
    shares: Dict[str, ShareInfo] = field(
        default_factory=dict
    )  # Maps ticker to ShareInfo
    history: List[Dict[str, Any]] = field(
        default_factory=list
    )  # History of portfolio changes
    currency: str = "EUR"  # Portfolio currency
    total_invested: float = field(init=False)  # Total amount invested in the portfolio
    symbol: str = field(init=False)  # Currency symbol

    def __post_init__(self):
        """
        Initialize the Portfolio instance by updating the currency symbol.

        Sets the `symbol` attribute to the symbol of the `currency` attribute.
        """
        self.symbol = get_symbol(self.currency) or ""
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
        date: Optional[str] = datetime.now().strftime("%Y-%m-%d"),
        fill: Optional[bool] = True,
    ) -> None:
        """
        Buys a security, adding it to the portfolio or updating existing volume.

        Args:
            ticker (str): The ticker of the security to buy
            volume (float): The volume of the security to buy
            currency (Optional[str]): The currency of the security. If None, defaults to portfolio currency
            price (Optional[float]): The price of the security. If None, will be fetched during update_portfolio
            date (Optional[str]): The date of the purchase. Default is current date
            fill (Optional[bool]): Whether to fetch security info from remote source
        """
        if ticker in self.securities:
            self.securities[ticker].buy(volume)
            logging.info(
                f"Bought {volume} units of existing security '{ticker}'. New number held: {round(self.securities[ticker].volume, 4)}."
            )
        else:
            # First time buying this security, create new Security instance
            new_security = Security(
                ticker=ticker,
                currency=currency if currency is not None else self.currency,
                price_in_security_currency=price if price is not None else 0.0,
                volume=volume,
                fill=fill if fill is not None else True,
            )
            self.securities[ticker] = new_security
            logging.info(
                f"Security '{ticker}' added to portfolio with volume {round(volume, 4)}."
            )

        # Register action in portfolio history
        self.history.append(
            {
                "ticker": ticker,
                "volume": volume,
                "date": date,
            }
        )

        # Update portfolio after buying security
        self.update_portfolio()

    def sell_security(
        self,
        ticker: str,
        volume: float,
        date: Optional[str] = datetime.now().strftime("%Y-%m-%d"),
    ) -> None:
        """
        Sells a volume of a security in the portfolio.

        Args:
            ticker (str): The ticker of the security to sell
            volume (float): The volume of the security to sell
            date (Optional[str]): The date of the sale. Default is current date

        Raises:
            ValueError: If the security is not found in the portfolio or if there is insufficient volume to sell.
        """
        if ticker not in self.securities:
            raise ValueError(f"Security '{ticker}' not found in portfolio")

        security = self.securities[ticker]
        if security.volume < volume:
            raise ValueError(
                f"Insufficient volume to sell. Available: {security.volume}, Requested: {volume}"
            )
        elif security.volume == volume:
            # Selling all units, remove security from portfolio and corresponding share
            del self.securities[ticker]
            self.shares.pop(ticker, None)
            logging.info(
                f"Sold all units of security '{ticker}'. Security removed from portfolio."
            )
        else:
            # Selling partial volume
            security.sell(volume)
            logging.info(
                f"Sold {volume} units of security '{ticker}'. New number held: {round(security.volume, 4)}."
            )

        # Register action in portfolio history
        self.history.append(
            {
                "ticker": ticker,
                "volume": -volume,
                "date": date,
            }
        )

        # Update portfolio after selling security
        self.update_portfolio()

    def get_portfolio_info(self) -> List[Dict[str, Any]]:
        """
        Returns a list of dictionaries containing information about each Security in the portfolio,
        including share information.

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
        - volume: float
        - volume_to_buy: float
        - amount_to_invest: float
        - value: float

        :return: List of dictionaries containing Security and share information.
        :rtype: List[Dict[str, Any]]
        """
        info_list = []
        for ticker, security in self.securities.items():
            info = security.get_info()
            share_info = self._get_share(ticker)
            info["target_share"] = share_info.target
            info["actual_share"] = share_info.actual
            info["final_share"] = share_info.final
            info_list.append(info)
        return info_list

    def verify_target_share_sum(self) -> bool:
        """
        Verifies if the target shares of all Securities in the portfolio sum to 1.

        Logs a warning if the sum is not equal to 1 and returns False.
        Logs an info message if the sum is equal to 1 and returns True.

        :return: True if the target shares sum to 1, False otherwise
        :rtype: bool
        """
        # Sum target shares from the shares mapping
        total_share = sum(share.target for share in self.shares.values())
        if abs(total_share - 1.0) > 1e-6:
            logging.warning(f"Portfolio shares do not sum to 1. (Sum: {total_share})")
            return False
        logging.info("Portfolio shares sum equal to 1. Portfolio is complete.")
        return True

    def set_target_share(self, ticker: str, share: float) -> None:
        """
        Sets the target share for a security in the portfolio.

        Args:
            ticker (str): The ticker of the security
            share (float): The target share to set (between 0 and 1)

        Raises:
            ValueError: If the security is not in the portfolio
        """
        if ticker not in self.securities:
            raise ValueError(f"Security '{ticker}' not found in portfolio")
        self._get_share(ticker).target = share

    def update_portfolio(self) -> None:
        """
        Update the portfolio by updating security prices and computing actual shares.
        It will raise an Exception if the portfolio is not complete.
        It first computes the total amount invested in the portfolio.
        Then it iterates over each Security in the portfolio, ensuring its price is in the portfolio currency,
        and computes its actual share based on the total invested.
        """
        # Update security prices
        for security in self.securities.values():
            security.update_security(self.currency)

        # Compute actual shares
        self.total_invested = sum(
            security.value for security in self.securities.values()
        )

        # Update actual shares
        if self.total_invested == 0:
            for ticker in self.securities:
                self._get_share(ticker).actual = 0.0
        else:
            for ticker, security in self.securities.items():
                self._get_share(ticker).actual = round(
                    security.value / self.total_invested, 4
                )

    def to_json(self, filepath: str) -> None:
        """
        Saves the portfolio to a JSON file.

        Args:
            filepath (str): Path to the JSON file to save the portfolio to.

        Raises:
            Exception: If an error occurs while saving the portfolio to JSON.
        """
        self.update_portfolio()  # Ensure shares are up to date
        try:
            data = self.to_dict()
            with open(filepath, "w") as f:
                json.dump(data, f, indent=4)
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
            return cls.from_dict(data)
        except Exception as e:
            logging.error(f"Error loading portfolio from JSON: {e}")
            return cls()

    def to_dict(self) -> Dict[str, Any]:
        """Return a JSON-serializable dict representing the portfolio."""
        securities_dict = {}
        for ticker, security in self.securities.items():
            security_info = security.get_info()
            share_info = self.shares[ticker].to_dict()
            # Combine security and share info
            security_info.update(share_info)
            securities_dict[ticker] = security_info

        return {
            "name": self.name,
            "currency": self.currency,
            "securities": securities_dict,
            "history": self.history,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Portfolio":
        """Create a Portfolio from a dict."""
        try:
            portfolio = cls(
                name=data.get("name", "Unnamed Portfolio"),
                currency=data.get("currency", "EUR"),
            )
            securities_data = data.get("securities", {})
            history_data = data.get("history", [])

            # Load securities and shares
            if isinstance(securities_data, dict):
                for ticker, security_data in securities_data.items():
                    # Extract share data
                    share_data = {
                        "target": security_data.get("target", 0.0),
                        "actual": security_data.get("actual", 0.0),
                        "final": security_data.get("final", 0.0),
                    }
                    # Create security
                    security = Security.from_json(security_data)
                    portfolio.securities[ticker] = security
                    # Create share info
                    portfolio.shares[ticker] = ShareInfo.from_dict(share_data)

            # Load history if history data
            portfolio.history = history_data if isinstance(history_data, list) else []

            # Update after instanciation (to get price in portfolio currency, and other attributes...)
            portfolio.update_portfolio()

            return portfolio
        except Exception as e:
            logging.error(f"Error creating Portfolio from dict: {e}")
            return cls()

    # --- Helper methods to centralize ShareInfo creation and access ---
    def _get_share(self, ticker: str) -> ShareInfo:
        """Return ShareInfo for ticker, creating it when missing."""
        if ticker not in self.shares:
            self.shares[ticker] = ShareInfo()
        return self.shares[ticker]

    def _load_shares(self, shares_data: Dict[str, Any]) -> None:
        """Populate self.shares from a mapping loaded from JSON.

        Expects shares_data to be a dict: ticker -> {target, actual, final}
        """
        if not isinstance(shares_data, dict):
            return
        for ticker, share_vals in shares_data.items():
            si = self._get_share(ticker)
            if isinstance(share_vals, dict):
                si.target = float(share_vals.get("target", si.target))
                si.actual = float(share_vals.get("actual", si.actual))
                si.final = float(share_vals.get("final", si.final))
