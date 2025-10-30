from foliotrack.Security import Security


def test_buy_security():
    """
    Test the buy method of Security.

    The buy method should increase the number of held units and the amount invested according \
        to the specified quantity and buy price.
    """
    security = Security(
        name="Security1",
        ticker="SEC1",
        currency="EUR",
        price_in_security_currency=100,
    )

    security.buy(10)
    assert security.quantity == 10
    assert security.value == 1000


def test_sell_security():
    """
    Test the sell method of Security.

    The sell method should decrease the number of held units and the amount invested according \
        to the specified quantity and sell price.
    """
    security = Security(
        name="Security1",
        ticker="SEC1",
        currency="EUR",
        price_in_security_currency=100,
    )

    security.buy(10)
    security.sell(4)
    assert security.quantity == 6
    assert security.value == 400


def test_update_security():
    """
    Test the update_price_from_yfinance method of Security.

    The method should update the Security price using yfinance based on its ticker, and update amount invested.
    """
    security = Security(
        name="Security1",
        ticker="SEC1",
        currency="EUR",
        price_in_security_currency=100,
    )
    security.update_security("EUR")
    assert security.price_in_security_currency > 0
    assert security.price_in_portfolio_currency > 0
