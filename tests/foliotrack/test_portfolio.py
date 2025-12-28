from foliotrack.Portfolio import Portfolio
import json
import os


def test_verify_target_share_sum():
    """
    Test the verify_target_share_sum method of a Portfolio.

    The method should return True if the target shares of all Securities in the Portfolio sum to 1.0.
    """
    portfolio = Portfolio(currency="EUR")
    portfolio.buy_security("SEC1", volume=10.0, price=100.0, fill=False)
    portfolio.buy_security("SEC2", volume=5.0, price=200.0, fill=False)
    portfolio.set_target_share("SEC1", 0.5)
    portfolio.set_target_share("SEC2", 0.5)

    assert portfolio.verify_target_share_sum() is True


def test_buy_security():
    """
    Test buying a Security in a Portfolio.

    Buying a Security in a Portfolio should increase the number held of the Security by the specified volume.
    The amount invested in the Security should be equal to the volume multiplied by the buy price.
    """
    portfolio = Portfolio(currency="EUR")
    portfolio.buy_security(
        "SEC1", volume=25.0, price=200.0, date="2023-02-14", fill=False
    )
    portfolio.set_target_share("SEC1", 1.0)

    assert portfolio.securities["SEC1"].volume == 25
    assert portfolio.securities["SEC1"].value == 5000

    # Assert history entry
    assert portfolio.history[-1]["ticker"] == "SEC1"
    assert portfolio.history[-1]["volume"] == 25
    assert portfolio.history[-1]["date"] == "2023-02-14"


def test_sell_security():
    """
    Test selling a Security in a Portfolio.

    Selling a Security in a Portfolio should decrease the number held of the Security by the specified volume.
    The amount invested in the Security should be updated accordingly.
    """
    portfolio = Portfolio(currency="EUR")
    portfolio.buy_security(
        "SEC1", volume=30.0, price=150.0, date="2023-02-14", fill=False
    )
    portfolio.buy_security(
        "SEC2", volume=5.0, price=100.0, date="2023-02-15", fill=False
    )
    portfolio.set_target_share("SEC1", 1.0)

    assert portfolio.securities["SEC1"].volume == 30
    assert portfolio.securities["SEC1"].value == 4500

    portfolio.sell_security("SEC1", volume=10.0)

    assert portfolio.securities["SEC1"].volume == 20
    assert portfolio.securities["SEC1"].value == 3000

    # Assert history log
    assert portfolio.history[-1]["ticker"] == "SEC1"
    assert portfolio.history[-1]["volume"] == -10
    assert portfolio.history[-1]["date"] == portfolio.history[-1]["date"]

    portfolio.sell_security("SEC2", volume=5.0)

    assert len(portfolio.securities) == 1  # SEC2 should be removed from portfolio
    assert "SEC2" not in portfolio.shares


def test_to_json():
    """
    Test saving a Portfolio to a JSON file.

    The to_json method should save the Portfolio to a JSON file with the correct structure and data.
    """
    portfolio = Portfolio(name="Test Portfolio", currency="EUR")

    portfolio.buy_security(
        "SEC1", volume=10.0, price=100.0, date="2023-02-14", fill=False
    )
    portfolio.set_target_share("SEC1", 1.0)

    filepath = "Portfolios/test_portfolio.json"
    portfolio.to_json(filepath)

    with open(filepath, "r") as f:
        data = json.load(f)

    assert data["name"] == "Test Portfolio"
    assert data["currency"] == "EUR"
    assert len(data["securities"]) == 1
    assert data["securities"]["SEC1"]["volume"] == 10
    assert data["securities"]["SEC1"]["value"] == 1000

    # Assert on target share
    assert data["securities"]["SEC1"]["target"] == 1.0

    # Assert on history log
    assert len(data["history"]) == 1
    assert data["history"][0]["ticker"] == "SEC1"
    assert data["history"][0]["volume"] == 10
    assert data["history"][0]["date"] == "2023-02-14"

    os.remove(filepath)


def test_from_json():
    """
    Test loading a Portfolio from a JSON file.

    The from_json method should load the Portfolio from a JSON file with the correct structure and data.
    """
    portfolio_data = {
        "name": "Test Portfolio",
        "currency": "EUR",
        "securities": {
            "SEC1": {
                "name": "Security1",
                "ticker": "SEC1",
                "currency": "EUR",
                "price_in_security_currency": 100,
                "volume": 10,
                "value": 1000,
                "fill": False,
            }
        },
        "history": [
            {"ticker": "SEC1", "volume": 20.0, "action": "buy", "date": "2023-02-14"},
            {"ticker": "SEC1", "volume": 10.0, "action": "sell", "date": "2024-12-25"},
        ],
    }

    filepath = "Portfolios/test_portfolio.json"
    with open(filepath, "w") as f:
        json.dump(portfolio_data, f)

    portfolio = Portfolio.from_json(filepath)

    assert portfolio.name == "Test Portfolio"
    assert portfolio.currency == "EUR"
    assert len(portfolio.securities) == 1
    assert portfolio.securities["SEC1"].name == "Security1"
    assert portfolio.securities["SEC1"].volume == 10
    assert portfolio.securities["SEC1"].value == 1000

    # Assert on history log
    assert len(portfolio.history) == 2
    assert portfolio.history[0]["ticker"] == "SEC1"
    assert portfolio.history[0]["volume"] == 20.0
    assert portfolio.history[0]["action"] == "buy"
    assert portfolio.history[0]["date"] == "2023-02-14"
    assert portfolio.history[1]["ticker"] == "SEC1"
    assert portfolio.history[1]["volume"] == 10.0
    assert portfolio.history[1]["action"] == "sell"
    assert portfolio.history[1]["date"] == "2024-12-25"

    os.remove(filepath)
