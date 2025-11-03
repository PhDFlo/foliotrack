import logging
import json
from typing import List, Optional, Dict, Any
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
    securities: List[Security] = field(
        default_factory=list
    )  # List of Securitys in the portfolio
    shares: Dict[str, ShareInfo] = field(
        default_factory=dict
    )  # Maps ticker to ShareInfo
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
        for security in self.securities:
            if security.ticker not in self.shares:
                self.shares[security.ticker] = ShareInfo()

    def buy_security(
        self,
        ticker,
        quantity: float,
        currency: Optional[str] = None,
        price: Optional[float] = None,
        fill: Optional[bool] = True,
    ) -> None:
        """
        Buys a security, adding it to the portfolio or updating existing quantity.

        Args:
            ticker (str): The ticker of the security to buy
            quantity (float): The quantity of the security to buy
            currency (Optional[str]): The currency of the security. If None, defaults to portfolio currency
            price (Optional[float]): The price of the security. If None, will be fetched during update_portfolio
            fill (Optional[bool]): Whether to fetch security info from remote source
        """
        # Check if security already exists in portfolio
        for p_sec in self.securities:
            if p_sec.ticker == ticker:
                p_sec.buy(quantity)
                # Update portfolio after buying security
                self.update_portfolio()
                logging.info(
                    f"Bought {quantity} units of existing security '{ticker}'. New number held: {round(p_sec.quantity, 4)}."
                )
                return

        # First time buying this security, create new Security instance
        new_security = Security(
            ticker=ticker,
            currency=currency if currency is not None else self.currency,
            price_in_security_currency=price if price is not None else 0.0,
            quantity=quantity,
            fill=fill if fill is not None else True,
        )
        self.securities.append(new_security)

        # Update portfolio after buying security
        self.update_portfolio()
        logging.info(
            f"Security '{ticker}' added to portfolio with quantity {round(quantity, 4)}."
        )

    def sell_security(self, ticker: str, quantity: float) -> None:
        """
        Sells a quantity of a security in the portfolio.

        Args:
            ticker (str): The ticker of the security to sell
            quantity (float): The quantity of the security to sell

        Raises:
            ValueError: If the security is not found in the portfolio or if there is insufficient quantity to sell.
        """
        for p_sec in self.securities:
            if p_sec.ticker == ticker:
                if p_sec.quantity < quantity:
                    raise ValueError(
                        f"Insufficient quantity to sell. Available: {p_sec.quantity}, Requested: {quantity}"
                    )
                elif p_sec.quantity == quantity:
                    # Selling all units, remove security from portfolio and corresponding share
                    self.securities = [
                        security
                        for security in self.securities
                        if security.ticker != ticker
                    ]
                    self.shares.pop(ticker, None)
                    # Update portfolio after removing security
                    self.update_portfolio()
                    logging.info(
                        f"Sold all units of security '{ticker}'. Security removed from portfolio."
                    )
                    return
                else:
                    # Selling partial quantity
                    p_sec.sell(quantity)
                    # Update portfolio after selling security
                    self.update_portfolio()
                    logging.info(
                        f"Sold {quantity} units of security '{ticker}'. New number held: {round(p_sec.quantity, 4)}."
                    )
                    return

        raise ValueError(f"Security '{ticker}' not found in portfolio")

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
        - quantity: float
        - number_to_buy: float
        - amount_to_invest: float
        - value: float

        :return: List of dictionaries containing Security and share information.
        :rtype: List[Dict[str, Any]]
        """
        info_list = []
        for security in self.securities:
            info = security.get_info()
            share_info = self._get_share(security.ticker)
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
        if not any(s.ticker == ticker for s in self.securities):
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
        for security in self.securities:
            security.update_security(self.currency)

        # Compute actual shares
        self.total_invested = sum(security.value for security in self.securities)

        # Update actual shares
        if self.total_invested == 0:
            for security in self.securities:
                self._get_share(security.ticker).actual = 0.0
        else:
            for security in self.securities:
                self._get_share(security.ticker).actual = round(
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
        # Ensure shares and securities are up to date
        # (do not call update_portfolio here to avoid side effects in to_dict)
        return {
            "currency": self.currency,
            "securities": [security.get_info() for security in self.securities],
            "shares": {ticker: info.to_dict() for ticker, info in self.shares.items()},
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Portfolio":
        """Create a Portfolio from a dict (the inverse of to_dict).

        This expects 'securities' to be a list of security dicts and 'shares' a mapping.
        """
        try:
            securities = [Security.from_json(sd) for sd in data.get("securities", [])]
            portfolio = cls(securities=securities, currency=data.get("currency", "EUR"))
            # Load shares mapping using ShareInfo.from_dict
            shares_data = data.get("shares", {})
            if isinstance(shares_data, dict):
                for ticker, sd in shares_data.items():
                    si = ShareInfo.from_dict(sd)
                    portfolio.shares[ticker] = si

            # Ensure every security has a ShareInfo
            for security in portfolio.securities:
                portfolio._get_share(security.ticker)

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
