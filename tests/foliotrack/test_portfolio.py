from foliotrack.Portfolio import Portfolio
from foliotrack.Security import Security
import json
import os


def test_add_security():
    """
    Test adding a Security to a Portfolio.

    Adding a Security to a Portfolio should increase the number of Securities in the Portfolio by 1.
    The added Security should be the first element in the list of Securities in the Portfolio.
    """
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
    """
    Test removing a Security from a Portfolio.

    Removing a Security from a Portfolio should decrease the number of securities in the Portfolio by 1.
    The removed Security should not be in the list of securities in the Portfolio.
    """
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
    """
    Test the verify_target_share_sum method of a Portfolio.

    The method should return True if the target shares of all Securities in the Portfolio sum to 1.0.
    """
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
    assert portfolio.verify_target_share_sum() is True


def test_buy_security():
    """
    Test buying a Security in a Portfolio.

    Buying a Security in a Portfolio should increase the number held of the Security by the specified quantity.
    The amount invested in the Security should be equal to the quantity multiplied by the buy price.
    """
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


def test_to_json():
    """
    Test saving a Portfolio to a JSON file.

    The to_json method should save the Portfolio to a JSON file with the correct structure and data.
    """
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

    filepath = "test_portfolio.json"
    portfolio.to_json(filepath)

    with open(filepath, "r") as f:
        data = json.load(f)

    assert data["currency"] == "EUR"
    assert len(data["securities"]) == 1
    assert data["securities"][0]["name"] == "Security1"
    assert data["securities"][0]["number_held"] == 10
    assert data["securities"][0]["amount_invested"] == 1000

    os.remove(filepath)


def test_from_json():
    """
    Test loading a Portfolio from a JSON file.

    The from_json method should load the Portfolio from a JSON file with the correct structure and data.
    """
    portfolio_data = {
        "currency": "EUR",
        "securities": [
            {
                "name": "Security1",
                "ticker": "SEC1",
                "currency": "EUR",
                "price_in_security_currency": 100,
                "target_share": 1.0,
                "number_held": 10,
                "amount_invested": 1000,
            }
        ],
        "staged_purchases": [],
    }

    filepath = "test_portfolio.json"
    with open(filepath, "w") as f:
        json.dump(portfolio_data, f)

    portfolio = Portfolio.from_json(filepath)

    assert portfolio.currency == "EUR"
    assert len(portfolio.securities) == 1
    assert portfolio.securities[0].name == "Security1"
    assert portfolio.securities[0].number_held == 10
    assert portfolio.securities[0].amount_invested == 1000

    os.remove(filepath)
