# This code is a Python module describing the ETFs (Exchange-Traded Funds) class.
import yfinance as yf


class ETF:
    """
    A class to represent an Exchange-Traded Fund (ETF).

    Attributes:
        name (str): The name of the ETF.
        ticker (str): The ticker symbol of the ETF.
        currency (str): The currency in which the ETF is traded.
        price (float): The current price of the ETF.
        yearly_charge (float): The annual charge (in percentage) associated with the ETF.
    """

    def __init__(
        self,
        name: str,
        ticker: str = "DCAM",
        currency: str = "EUR",
        price: float = 500.0,
        yearly_charge: float = 0.2,
    ):
        """
        Initialize an ETF instance.

        Args:
            name (str): The name of the ETF.
            ticker (str, optional): The ticker symbol. Defaults to "DCAM".
            currency (str, optional): The trading currency. Defaults to "EUR".
            price (float, optional): The price of the ETF. Defaults to 500.0.
            yearly_charge (float, optional): The annual charge in percent. Defaults to 0.2.
        """
        self.name = name
        self.ticker = ticker
        self.currency = currency
        self.price = price
        self.yearly_charge = yearly_charge
        # Verify currency
        if self.currency.lower() not in ["eur", "usd"]:
            print(
                f"Error: Currency '{self.currency}' is not supported. Only EUR and USD are allowed."
            )
        # Set symbol based on currency
        if self.currency.lower() in ["eur", "€"]:
            self.symbol = "€"
        elif self.currency.lower() in ["usd", "$"]:
            self.symbol = "$"
        else:
            self.symbol = ""

    def __repr__(self):
        """
        Return a string representation of the ETF instance.

        Returns:
            str: String representation of the ETF.
        """
        return (
            f"ETF(name={self.name}, ticker={self.ticker}, currency={self.currency}, "
            f"price={self.price}{self.symbol}, yearly_charge={self.yearly_charge}"
        )

    def get_info(self):
        """
        Get a dictionary containing the ETF's information.

        Returns:
            dict: A dictionary with ETF attributes.
        """
        return {
            "name": self.name,
            "ticker": self.ticker,
            "currency": self.currency,
            "symbol": self.symbol,
            "price": f"{self.price}",
            "yearly_charge": f"{self.yearly_charge}",
        }

    def update_price_from_yfinance(self):
        """
        Update the ETF price using yfinance based on its ticker.
        """
        ticker = yf.Ticker(self.ticker)
        try:
            price = ticker.info.get("regularMarketPrice")
            if price is not None:
                self.price = price
        except Exception as e:
            print(f"Could not update price for {self.ticker}: {e}")
