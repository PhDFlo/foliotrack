import pytest
from PBalance.Security import Security


def test_buy_security():
    security = Security(
        name="Security1",
        ticker="SEC1",
        currency="EUR",
        price_in_security_currency=100,
        target_share=0.5,
    )
    security.buy(10, buy_price=100)
    assert security.number_held == 10
    assert security.amount_invested == 1000


def test_compute_actual_share():
    security = Security(
        name="Security1",
        ticker="SEC1",
        currency="EUR",
        price_in_security_currency=100,
        target_share=0.5,
    )
    security.buy(10, buy_price=100)
    security.compute_actual_share(2000)
    assert security.actual_share == 0.5


def test_update_price_from_yfinance():
    security = Security(
        name="Security1",
        ticker="SEC1",
        currency="EUR",
        price_in_security_currency=100,
        target_share=0.5,
    )
    security.update_price_from_yfinance()
    assert security.price_in_security_currency > 0


def test_compute_price_in_portfolio_currency():
    security = Security(
        name="Security1",
        ticker="SEC1",
        currency="USD",
        price_in_security_currency=100,
        target_share=0.5,
    )
    security.compute_price_in_portfolio_currency("EUR")
    assert security.price_in_portfolio_currency > 0
