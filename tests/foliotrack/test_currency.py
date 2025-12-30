from foliotrack.utils.Currency import Currency


def test_get_symbol():
    """
    Tests the get_symbol function in Currency class.

    Verifies that function returns correct symbols for given currency codes.
    """
    currency = Currency()
    assert currency.get_symbol("USD") == "$"
    assert currency.get_symbol("EUR") == "€"
    assert currency.get_symbol("JPY") == "¥"


def test_get_currency_name():
    """
    Tests the get_currency_name function in Currency class.

    Verifies that function returns correct names for given currency codes.
    """
    currency = Currency()
    assert currency.get_currency_name("USD") == "United States dollar"
    assert currency.get_currency_name("EUR") == "European Euro"
    assert currency.get_currency_name("JPY") == "Japanese yen"


def test_get_currency_code_from_symbol():
    """
    Tests the get_currency_code_from_symbol function in Currency class.

    Verifies that function returns correct currency codes for given symbols.
    """
    currency = Currency()
    assert currency.get_currency_code_from_symbol("$") == "USD"
    assert currency.get_currency_code_from_symbol("€") == "EUR"
    assert currency.get_currency_code_from_symbol("¥") == "CNY"


def test_get_rate_between():
    """
    Tests the get_rate_between function in Currency class.

    Verifies that function returns correct rates for given currency codes.
    """
    currency = Currency()
    assert currency.get_rate_between("USD", "EUR") > 0
    assert currency.get_rate_between("EUR", "JPY") > 0
    assert currency.get_rate_between("JPY", "USD") > 0
