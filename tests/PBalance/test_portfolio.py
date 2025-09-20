from PBalance.Portfolio import Portfolio
from PBalance.Security import Security


def test_add_security():
    portfolio = Portfolio(currency="EUR")
    security = Security(
        name="Security1",
        ticker="SEC1",
        currency="EUR",
        price_in_security_currency=100,
        target_share=0.5,
    )
    portfolio.add_security(security)
    assert len(portfolio.securities) == 1
    assert portfolio.securities[0].name == "Security1"


def test_remove_security():
    portfolio = Portfolio(currency="EUR")
    security1 = Security(
        name="Security1",
        ticker="SEC1",
        currency="EUR",
        price_in_security_currency=100,
        target_share=0.5,
    )
    security2 = Security(
        name="Security2",
        ticker="SEC2",
        currency="EUR",
        price_in_security_currency=200,
        target_share=0.5,
    )
    portfolio.add_security(security1)
    portfolio.add_security(security2)
    portfolio.remove_security("SEC1")
    assert len(portfolio.securities) == 1
    assert portfolio.securities[0].name == "Security2"


def test_verify_target_share_sum():
    portfolio = Portfolio(currency="EUR")
    security1 = Security(
        name="Security1",
        ticker="SEC1",
        currency="EUR",
        price_in_security_currency=100,
        target_share=0.5,
    )
    security2 = Security(
        name="Security2",
        ticker="SEC2",
        currency="EUR",
        price_in_security_currency=200,
        target_share=0.5,
    )
    portfolio.add_security(security1)
    portfolio.add_security(security2)
    assert portfolio.verify_target_share_sum() == True


def test_buy_security():
    portfolio = Portfolio(currency="EUR")
    security = Security(
        name="Security1",
        ticker="SEC1",
        currency="EUR",
        price_in_security_currency=100,
        target_share=1.0,
    )
    portfolio.add_security(security)
    portfolio.buy_security("SEC1", 10, buy_price=100)
    assert portfolio.securities[0].number_held == 10
    assert portfolio.securities[0].amount_invested == 1000
