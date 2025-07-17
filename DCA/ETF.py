# This code is a Python module describing the ETFs (Exchange-Traded Funds) class.


class ETF:
    """
    A class to represent an Exchange-Traded Fund (ETF).

    Attributes:
        name (str): The name of the ETF.
        ticker (str): The ticker symbol of the ETF.
        currency (str): The currency in which the ETF is traded.
        price (float): The current price of the ETF.
        fees (float): The annual fees (in percentage) associated with the ETF.
    """

    def __init__(
        self,
        name: str,
        ticker: str = "DCAM",
        currency: str = "Euro",
        price: float = 500.0,
        fees: float = 0.2,
    ):
        """
        Initialize an ETF instance.

        Args:
            name (str): The name of the ETF.
            ticker (str, optional): The ticker symbol. Defaults to "DCAM".
            currency (str, optional): The trading currency. Defaults to "Euro".
            price (float, optional): The price of the ETF. Defaults to 500.0.
            fees (float, optional): The annual fees in percent. Defaults to 0.2.
        """
        self.name = name
        self.ticker = ticker
        self.currency = currency
        self.price = price
        self.fees = fees

    def __repr__(self):
        """
        Return a string representation of the ETF instance.

        Returns:
            str: String representation of the ETF.
        """
        return (
            f"ETF(name={self.name}, ticker={self.ticker}, currency={self.currency}, "
            f"price={self.price}€, fees={self.fees}"
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
            "price": f"{self.price}€",
            "fees": f"{self.fees}",
        }
