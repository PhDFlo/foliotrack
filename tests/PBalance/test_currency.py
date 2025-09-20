import pytest
from PBalance.Currency import Currency


def test_get_symbol():
    currency = Currency()
    assert currency.get_symbol("USD") == "$"
    assert currency.get_symbol("EUR") == "€"
    assert currency.get_symbol("JPY") == "¥"


def test_get_currency_name():
    currency = Currency()
    assert currency.get_currency_name("USD") == "United States dollar"
    assert currency.get_currency_name("EUR") == "European Euro"
    assert currency.get_currency_name("JPY") == "Japanese yen"


def test_get_currency_code_from_symbol():
    currency = Currency()
    assert currency.get_currency_code_from_symbol("$") == "ARS"
    assert currency.get_currency_code_from_symbol("€") == "EUR"
    assert currency.get_currency_code_from_symbol("¥") == "CNY"


def test_get_rate_between():
    currency = Currency()
    assert currency.get_rate_between("USD", "EUR") > 0
    assert currency.get_rate_between("EUR", "JPY") > 0
    assert currency.get_rate_between("JPY", "USD") > 0
