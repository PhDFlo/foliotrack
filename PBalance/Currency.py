import json, os
import pandas as pd
from ecbdata import ecbdata


class Currency:

    def __init__(self):
        self.__currency_data = None

    @property
    def _currency_data(self):
        if self.__currency_data is None:
            file_path = os.path.dirname(os.path.abspath(__file__))
            with open(file_path + '/data/currencies.json', encoding="utf-8") as f:
                self.__currency_data = json.loads(f.read())
        return self.__currency_data

    def _get_data(self, currency_code):
        currency_dict = next((item for item in self._currency_data if item["cc"] == currency_code), None)
        return currency_dict

    def _get_data_from_symbol(self, symbol):
        currency_dict = next((item for item in self._currency_data if item["symbol"] == symbol), None)
        return currency_dict

    def get_symbol(self, currency_code):
        currency_dict = self._get_data(currency_code)
        if currency_dict:
            return currency_dict.get('symbol')
        return None

    def get_currency_name(self, currency_code):
        currency_dict = self._get_data(currency_code)
        if currency_dict:
            return currency_dict.get('name')
        return None

    def get_currency_code_from_symbol(self, symbol):
        currency_dict = self._get_data_from_symbol(symbol)
        if currency_dict:
            return currency_dict.get('cc')
        return None
    
    def get_rate_between(self, from_currency: str, to_currency: str, date: str = None) -> float:
        """
        Returns the exchange rate from `from_currency` to `to_currency`
        using ECB reference rates.

        E.g., from_currency = 'JPY', to_currency = 'USD' gives how many USD per JPY.

        If date is None, uses the latest available rate.
        Date format: 'YYYY-MM-DD'.
        """
        # Normalize currency codes
        from_currency = from_currency.upper()
        to_currency = to_currency.upper()

        # If one of the currencies is EUR, then it's simpler
        if from_currency == 'EUR' and to_currency == 'EUR':
            return 1.0

        # Build series keys to get rates vs EUR
        # Key format: frequency.currency.EUR.SP00.A
        freq = 'EXR.D'
        series_key_from = f"{freq}.{from_currency}.EUR.SP00.A"
        series_key_to   = f"{freq}.{to_currency}.EUR.SP00.A"

        # Fetch the two series
        # If a specific date is given, we restrict to that date; else get the latest
        if date:
            # Do not call ecbdata.get_series for EUR — we treat EUR as known (1.0)
            df_from = pd.DataFrame() if from_currency == 'EUR' else ecbdata.get_series(series_key_from, start=date, end=date)
            df_to   = pd.DataFrame() if to_currency == 'EUR' else ecbdata.get_series(series_key_to,   start=date, end=date)
        else:
            # Only fetch series for non-EUR currencies
            df_from = pd.DataFrame() if from_currency == 'EUR' else ecbdata.get_series(series_key_from, start='2025-01-01')
            df_to   = pd.DataFrame() if to_currency == 'EUR' else ecbdata.get_series(series_key_to,   start='2025-01-01')

        # The dataframes have columns like TIME_PERIOD and OBS_VALUE
        # Convert to proper float & align
        def extract_rate(df, currency):
            if df.empty:
                raise ValueError(f"No data found for currency {currency} on date {date or 'latest'}")
            # Use the last available row
            row = df.iloc[-1]
            rate = float(row['OBS_VALUE'])
            return rate

        rate_from = None
        rate_to   = None

        # If from_currency is EUR, then rate_from = 1
        if from_currency == 'EUR':
            rate_from = 1.0
        else:
            rate_from = extract_rate(df_from, from_currency)

        if to_currency == 'EUR':
            rate_to = 1.0
        else:
            rate_to = extract_rate(df_to, to_currency)

        # Now: want rate from from_currency → to_currency
        # ECB gives: OBS_VALUE = how many units of that currency per 1 EUR
        #
        # So:
        #   1 EUR = rate_from units of from_currency  → 1 unit of from_currency = 1 / rate_from EUR
        #   1 EUR = rate_to   units of to_currency    → 1 EUR = rate_to to_currency
        #
        # Thus:
        #   1 unit of from_currency = (1 / rate_from) * rate_to units of to_currency
        #
        cross_rate = (1 / rate_from) * rate_to
        return cross_rate


_CURRENCY_CODES = Currency()

get_symbol = _CURRENCY_CODES.get_symbol
get_currency_name = _CURRENCY_CODES.get_currency_name
get_currency_code_from_symbol = _CURRENCY_CODES.get_currency_code_from_symbol
get_rate_between = _CURRENCY_CODES.get_rate_between