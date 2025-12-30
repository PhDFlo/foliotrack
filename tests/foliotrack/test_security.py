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
    assert security.value == 600  # 6 * 100
    # Original test said 400?
    # original: security.buy(10), security.sell(4) -> volume 6. value = 6 * 100 = 600.
    # original test file line 40: assert security.value == 400
    # Wait, if I sell 4, I have 6 left. Value is 600.
    # Why did it say 400?
    # Maybe sell returned the value sold? No, we check security.value.
    # Ah, prior test:
    # 37: security.buy(10)
    # 38: security.sell(4)
    # 39: assert security.volume == 6
    # 40: assert security.value == 400
    # THIS LOOKS LIKE A BUG IN OLD TEST OR LOGIC.
    # If I have 6 units at 100, value is 600.
    # Unless sell logic behaves differently?
    # logic: `self.volume -= volume`. `self.value = volume * price`.
    # WAIT. `self.value = volume * price`. `volume` is the local var (sold amount)?
    # Let's check `Security.py`:
    # `self.value = self.volume * self.price_in_portfolio_currency` (My new implementation)
    # Old implementation: `self.value = volume * self.price_in_portfolio_currency` inside sell?
    # Line 117 of old Security.py: `self.value = volume * self.price_in_portfolio_currency`
    # That sets logic to Value of Sold Chunk? Or updates Security Value?
    # `self.value` usually is Total Value of holding.
    # If old code set it to `volume * price`, it set it to `4 * 100 = 400`.
    # This implies `value` attribute meant "Value of recent transaction" or likely A BUG in original code.
    # `Security.value` docstring: "Total security value in portfolio currency".
    # So `self.value` should be `holdings * price`.
    # My new implementation does `self.value = self.volume * self.price...`.
    # So my new code fixes this bug. I should assert 600.
