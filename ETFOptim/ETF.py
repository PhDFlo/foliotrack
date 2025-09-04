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
        target_share: float = 1.0,
        number_held: float = 0.0,
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
        self.target_share = target_share
        self.number_held = number_held
        self.amount_invested = self.number_held * self.price
        self.actual_share = 0.0
        self.number_to_buy = 0.0
        self.amount_to_invest = 0.0
        self.final_share = 0.0
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
            "target_share": self.target_share,
            "number_held": f"{self.number_held}",
            "amount_invested": f"{self.amount_invested}",
            "actual_share": self.actual_share,
            "number_to_buy": self.number_to_buy,
            "amount_to_invest": f"{self.amount_to_invest}",
            "final_share": self.final_share,
        }

    def buy(self, quantity: float, buy_price: float = None, fee: float = 0.0, date: str = None):
        import datetime
        if date is None:
            date = datetime.datetime.now().strftime("%Y-%m-%d")
        if buy_price is None:
            buy_price = self.price
        self.number_held += quantity
        self.amount_invested += quantity * buy_price
        # Optionally, update actual_share, number_to_buy, etc. externally
        return {
            "ticker": self.ticker,
            "quantity": quantity,
            "buy_price": buy_price,
            "fee": fee,
            "date": date,
        }

    def compute_actual_share(self, total_invested: float):
        if total_invested == 0:
            self.actual_share = 0.0
        else:
            self.actual_share = round(self.amount_invested / total_invested, 2)

    def update_price_from_yfinance(self):
        import yfinance as yf
        ticker = yf.Ticker(self.ticker)
        try:
            price = ticker.info.get("regularMarketPrice")
            if price is not None:
                self.price = price
                self.amount_invested = self.number_held * self.price
        except Exception as e:
            print(f"Could not update price for {self.ticker}: {e}")

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
