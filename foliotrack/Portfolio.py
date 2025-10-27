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

    def add_security(self, security: Security, target_share: float = 0.0) -> None:
        """
        Adds a Security to the portfolio.

        Args:
            security (Security): Security instance to add to the portfolio.
            target_share (float): Target share for the security in the portfolio. Defaults to 0.0.

        Logs a message indicating the Security has been added with its target share and number held.
        """
        self.securities.append(security)
        # Ensure share info exists for this ticker before assigning
        if security.ticker not in self.shares:
            self.shares[security.ticker] = ShareInfo()
        self.shares[security.ticker].target = target_share
        logging.info(
            f"Security '{security.name}' added to portfolio with share {target_share} and number held {round(security.quantity, 4)}."
        )

    # Need to validate this method with two test cases (one where security exists, one where it does not) and validate add sell_security method. Also remove remove_security method
    def buy_security(
        self, security: Security, target_share: Optional[float] = None
    ) -> None:
        """
        Buys a security, adding it to the portfolio or updating existing quantity.

        Args:
            security (Security): The security to buy
            target_share (Optional[float]): Target share for the security if it's new
        """
        for p_sec in self.securities:
            if p_sec.ticker == security.ticker:
                p_sec.quantity = p_sec.quantity + security.quantity
                if target_share is not None:
                    self.set_target_share(security.ticker, target_share)
                # Update portfolio after buying security
                self.update_portfolio()
                return

        self.securities.append(security)
        # If adding new security, initialize target share
        if target_share is None:
            target_share = 0.0  # Default to 0 if not specified
        # Ensure share info exists for this ticker before assigning
        if security.ticker not in self.shares:
            self.shares[security.ticker] = ShareInfo()
        self.shares[security.ticker].target = target_share

        self.update_portfolio()
        logging.info(
            f"Security '{security.name}' added to portfolio with share {target_share} and number held {round(security.quantity, 4)}."
        )

    def sell_security(self, ticker: str, quantity: float) -> None:
        """
        Sells a specified quantity of a Security in the portfolio, updating number held and amount invested.

        Args:
            ticker (str): The ticker of the Security to sell.
            quantity (float): The quantity of the Security to sell.
        """
        for security in self.securities:
            if security.ticker == ticker:
                if quantity > security.quantity:
                    logging.error(
                        f"Cannot sell {quantity} units of '{ticker}'. Only {security.quantity} units held."
                    )
                    raise ValueError(
                        f"Cannot sell {quantity} units of '{ticker}'. Only {security.quantity} units held."
                    )
                elif quantity == security.quantity:
                    self.securities = [
                        security
                        for security in self.securities
                        if security.ticker != ticker
                    ]
                    logging.info(f"Sold all units of '{ticker}'.")
                else:
                    security.quantity -= quantity
                    self.update_portfolio()
                    logging.info(
                        f"Sold {quantity} units of '{ticker}'. New number held: {security.quantity}."
                    )

                # Update portfolio
                self.update_portfolio()

                return
        logging.error(f"Security '{ticker}' not found in the portfolio.")
        raise ValueError(f"Security '{ticker}' not found in the portfolio.")

    def remove_security(self, ticker: str) -> None:
        """
        Removes a Security from the portfolio.

        Args:
            ticker (str): Ticker of the Security to remove from the portfolio.

        Logs a message indicating the Security has been removed.
        """
        self.securities = [
            security for security in self.securities if security.ticker != ticker
        ]

    def get_portfolio_info(self) -> List[Dict[str, Any]]:
        """
        Returns a list of dictionaries containing information about each Security in the portfolio.

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
        - amount_invested: float

        :return: List of dictionaries containing Security information.
        :rtype: List[Dict[str, Any]]
        """
        return [security.get_info() for security in self.securities]

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
        self.shares[ticker].target = share

    def distribute_remaining_share(
        self, excluded_tickers: Optional[List[str]] = None
    ) -> None:
        """
        Evenly distributes the remaining share (1 - sum of fixed shares) among non-excluded securities.

        Args:
            excluded_tickers (Optional[List[str]]): List of tickers to exclude from distribution
        """
        if excluded_tickers is None:
            excluded_tickers = []

        # Calculate remaining share
        fixed_share = sum(
            share.target
            for ticker, share in self.shares.items()
            if ticker in excluded_tickers
        )
        remaining_share = 1.0 - fixed_share

        # Get number of securities to distribute remaining share among
        distribute_tickers = [
            s.ticker for s in self.securities if s.ticker not in excluded_tickers
        ]
        if not distribute_tickers:
            return

        # Distribute remaining share evenly
        share_per_security = remaining_share / len(distribute_tickers)
        for ticker in distribute_tickers:
            self.shares[ticker].target = share_per_security

    # def buy_security(
    #     self,
    #     security_ticker: str,
    #     quantity: float,
    #     buy_price: Optional[float] = None,
    #     fee: float = 0.0,
    #     date: Optional[str] = None,
    # ) -> None:
    #     """
    #     Buys a specified quantity of a Security in the portfolio, updating number held and amount invested.

    #     Args:
    #         security_ticker (str): The ticker of the Security to buy.
    #         quantity (float): The quantity of the Security to buy.
    #         buy_price (Optional[float], optional): The price at which the Security is bought. Defaults to None.
    #         fee (float, optional): The fee associated with the purchase. Defaults to 0.0.
    #         date (Optional[str], optional): The date of the purchase. Defaults to None.

    #     Raises:
    #         ValueError: If the Security is not found in the portfolio.
    #     """
    #     for security in self.securities:
    #         if security.ticker == security_ticker:
    #             purchase = security.buy(quantity, buy_price, fee, date)
    #             self.update_portfolio()
    #             self.staged_purchases.append(purchase)
    #             logging.info(
    #                 f"Bought {quantity} units of '{security_ticker}' on {purchase['date']}. New number held: {security.quantity}."
    #             )
    #             return
    #     logging.error(f"Security '{security_ticker}' not found in the portfolio.")
    #     raise ValueError(f"Security '{security_ticker}' not found in the portfolio.")

    def update_portfolio(self) -> None:
        """
        Update the portfolio by updating security prices and computing actual shares.
        It will raise an Exception if the portfolio is not complete.
        It first computes the total amount invested in the portfolio.
        Then it iterates over each Security in the portfolio, ensuring its price is in the portfolio currency,
        and computes its actual share based on the total invested.
        """
        if not self.verify_target_share_sum():
            raise Exception("Error, the portfolio is not complete.")

        # Update security prices
        for security in self.securities:
            security.update_prices(self.currency)

        # Compute actual shares
        self.total_invested = sum(
            security.amount_invested for security in self.securities
        )

        # Update actual shares
        if self.total_invested == 0:
            for security in self.securities:
                self.shares[security.ticker].actual = 0.0
        else:
            for security in self.securities:
                self.shares[security.ticker].actual = round(
                    security.amount_invested / self.total_invested, 4
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
            data = {
                "currency": self.currency,
                # Serialize securities using their own to_json / get_info method
                "securities": [security.get_info() for security in self.securities],
                # Serialize shares mapping (target/actual/final) per ticker
                "shares": {
                    ticker: {
                        "target": info.target,
                        "actual": info.actual,
                        "final": info.final,
                    }
                    for ticker, info in self.shares.items()
                },
            }
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

            # Deserialize securities
            securities = [
                Security.from_json(security_data)
                for security_data in data.get("securities", [])
            ]

            portfolio = cls(securities=securities, currency=data.get("currency", "EUR"))

            # Load shares mapping (new data format expects a 'shares' dict)
            shares_data = data.get("shares", {})
            if isinstance(shares_data, dict):
                for ticker, share_vals in shares_data.items():
                    # Ensure a ShareInfo exists for this ticker
                    if ticker not in portfolio.shares:
                        portfolio.shares[ticker] = ShareInfo()
                    self_share = portfolio.shares[ticker]

                    # Expect a dict with target/actual/final values
                    if isinstance(share_vals, dict):
                        self_share.target = float(
                            share_vals.get("target", self_share.target)
                        )
                        self_share.actual = float(
                            share_vals.get("actual", self_share.actual)
                        )
                        self_share.final = float(
                            share_vals.get("final", self_share.final)
                        )

            # If no shares mapping was provided, ensure all securities have ShareInfo entries
            for security in portfolio.securities:
                if security.ticker not in portfolio.shares:
                    portfolio.shares[security.ticker] = ShareInfo()

            return portfolio
        except Exception as e:
            logging.error(f"Error loading portfolio from JSON: {e}")
            return cls()
