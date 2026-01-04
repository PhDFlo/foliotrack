from foliotrack.domain.Security import Security


def test_buy_security():
    """
    Test the buy method of Security.
    """
    security = Security(
        name="Security1",
        ticker="SEC1",
        currency="EUR",
        price_in_security_currency=100,
    )

    security.buy(10)
    assert security.volume == 10
    assert security.value == 1000


def test_sell_security():
    """
    Test the sell method of Security.
    """
    security = Security(
        name="Security1",
        ticker="SEC1",
        currency="EUR",
        price_in_security_currency=100,
    )

    security.buy(10)
    security.sell(4)
    assert security.volume == 6
    assert security.value == 600
