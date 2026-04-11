import os
import pandas as pd
from pathlib import Path
import pytest
from streamlit.testing.v1.app_test import AppTest


@pytest.fixture
def page_file():
    return "pages/equilibrium_buy.py"


@pytest.fixture
def dashboard_dir():
    return str(Path(__file__).parent.parent.parent.parent / "foliotrack" / "dashboard")


@pytest.fixture
def original_dir(dashboard_dir):
    original = os.getcwd()
    os.chdir(dashboard_dir)
    yield original
    os.chdir(original)


def test_edit_investment(page_file, original_dir):
    """Increment investment amount and minimum percentage inputs"""
    at = AppTest.from_file("app.py").run()

    # Switch to the load_portfolio page to render it within the full app
    at.switch_page(page_file)
    at.run()

    # Increment Invesment Amount input
    at.number_input(key="investment_amount").increment().run()
    assert at.number_input(key="investment_amount").value == pytest.approx(
        500.01, 0.001
    )

    # Increment Minimum Percentage input
    at.number_input(key="min_percent").increment().run()
    assert at.number_input(key="min_percent").value == pytest.approx(1.0, 0.001)


def test_optimize_portfolio(page_file, original_dir):
    """Click Optimize Portfolio button"""
    at = AppTest.from_file("app.py").run()

    # Switch to the load_portfolio page to render it within the full app
    at.switch_page("pages/load_portfolio.py")
    at.run()

    # Load a portfolio first
    at.selectbox(key="portfolio_file_select").set_value("investment_example.json").run()
    at.button(key="load").click().run()

    # Switch to the equilibrium_buy page
    at.switch_page(page_file)
    at.run()

    # Change investment amount and minimum percentage
    at.number_input(key="investment_amount").set_value(1000.0).run()
    at.number_input(key="min_percent").set_value(0.95).run()
    at.number_input(key="max_diff_sec").set_value(3).run()

    # Click on the "Optimize Portfolio" button
    at.button(key="optimize_button").click().run()

    expected_df = pd.DataFrame(
        {
            "Volume to buy": [1, 1, 1],
        }
    )

    assert (
        at.dataframe[0].value["Volume to buy"].equals(expected_df["Volume to buy"])
    ), (
        f"Mismatch in 'Volume to buy' column. Got: {at.dataframe[0].value['Volume to buy'].tolist()}"
    )
