import os
import pandas as pd
from pathlib import Path
import pytest
from streamlit.testing.v1.app_test import AppTest


@pytest.fixture
def page_file():
    return "pages/load_portfolio.py"


@pytest.fixture
def dashboard_dir():
    return str(Path(__file__).parent.parent.parent.parent / "foliotrack" / "dashboard")


@pytest.fixture
def original_dir(dashboard_dir):
    original = os.getcwd()
    os.chdir(dashboard_dir)
    yield original
    os.chdir(original)


def test_select_and_load_file(page_file, original_dir):
    """Select a portfolio file and click Load (or Refresh)"""
    # Initialize the app test with the main app so pages and sidebar are registered
    at = AppTest.from_file("app.py").run()

    # Switch to the load_portfolio page to render it within the full app
    at.switch_page(page_file)
    at.run()

    # There should be a selectbox for portfolio files
    assert at.selectbox, "No selectbox found on load_portfolio page"

    # Select default file (e.g. investment_example.json)
    at.selectbox(key="portfolio_file_select").set_value("investment_example.json").run()

    # Click on the "Load" button
    at.button(key="load").click().run()

    expected_df = pd.DataFrame(
        {
            "Name": [
                "Airbus SE",
                "NVIDIA Corporation",
                "LVMH Mo\u00ebt Hennessy - Louis Vuitton, Soci\u00e9t\u00e9 Europ\u00e9enne",
            ],
            "Ticker": ["AIR.PA", "NVDA", "MC.PA"],
            "Currency": ["EUR", "USD", "EUR"],
            "Price": [195.72, 183.31, 627.7],
            "Actual Share": [0.8093, 0.038, 0.1527],
            "Target Share": [0.5, 0.2, 0.3],
            "Volume": [17.0, 1.0, 1.0],
        }
    )

    for key in expected_df.keys():
        assert at.dataframe[0].value[key].equals(expected_df[key]), (
            f"Mismatch in column {key}"
        )


def test_update_security_price(page_file, original_dir):
    """Select a portfolio file and click Load (or Refresh)"""
    # Initialize the app test with the main app so pages and sidebar are registered
    at = AppTest.from_file("app.py").run()

    # Switch to the load_portfolio page to render it within the full app
    at.switch_page(page_file)
    at.run()

    # Select default file (e.g. investment_example.json)
    at.selectbox(key="portfolio_file_select").set_value("investment_example.json").run()

    # Click on the "Load" button
    at.button(key="load").click().run()

    # Click on the "Update Securities Price" button
    at.button(key="update_securities_price").click().run()

    # Check that prices have been updated (not equal to initial values)
    updated_prices = at.dataframe[0].value["Price"]
    initial_prices = [500.0, 300.0, 200.0]
    assert not updated_prices.equals(pd.Series(initial_prices)), (
        "Prices were not updated"
    )


def test_buy_sell_security(page_file, original_dir):
    """Select a portfolio file, load it, buy and sell a security"""
    # Initialize the app test with the main app so pages and sidebar are registered
    at = AppTest.from_file("app.py").run()

    # Switch to the load_portfolio page to render it within the full app
    at.switch_page(page_file)
    at.run()

    # Select default file (e.g. investment_example.json)
    at.selectbox(key="portfolio_file_select").set_value("investment_example.json").run()

    # Click on the "Load" button
    at.button(key="load").click().run()

    # Buy 2 shares of NVIDIA Corporation
    at.selectbox(key="ticker_buy_choice").set_value("NVDA").run()
    at.number_input(key="buy_volume").set_value(2).run()
    at.date_input(key="buy_date").set_value("2023-01-01").run()
    at.button(key="buy_button").click().run()

    # Check that volumes have been updated
    assert at.dataframe[0].value.set_index("Ticker")["Volume"]["NVDA"] == 3.0, (
        "Buy operation failed"
    )

    # Sell 1 share of Airbus SE
    at.selectbox(key="ticker_sell_choice").set_value("AIR.PA").run()
    at.number_input(key="sell_volume").set_value(1).run()
    at.button(key="sell_button").click().run()

    # Check that quantities have been updated
    assert at.dataframe[0].value.set_index("Ticker")["Volume"]["AIR.PA"] == 16.0, (
        "Sell operation failed"
    )


def test_save_file(page_file, original_dir):
    """Select a portfolio file, load it, modify it and save it"""
    # Creates save file as selectox options must exist in Apptest
    filepath = "./Portfolios/investment_test.json"
    with open(filepath, "w"):
        pass

    # Initialize the app test with the main app so pages and sidebar are registered
    at = AppTest.from_file("app.py").run()

    # Switch to the load_portfolio page to render it within the full app
    at.switch_page(page_file)
    at.run()

    # Select default file (e.g. investment_example.json)
    at.selectbox(key="portfolio_file_select").set_value("investment_example.json").run()

    # Click on the "Load" button
    at.button(key="load").click().run()

    # Modify the save filename
    at.selectbox(key="portfolio_file_save").set_value("investment_test.json").run()

    # Click on the "Save" button
    at.button(key="save_button").click().run()

    assert os.path.exists(filepath), "Saved file does not exist"

    # Clean up
    os.remove(filepath)
