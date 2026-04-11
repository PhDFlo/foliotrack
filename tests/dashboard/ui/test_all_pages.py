import os
from pathlib import Path
import pytest
from streamlit.testing.v1.app_test import AppTest


@pytest.fixture
def dashboard_dir():
    """Point cwd to the dashboard package so Streamlit resolves pages correctly."""
    return str(Path(__file__).parent.parent.parent.parent / "foliotrack" / "dashboard")


@pytest.fixture
def original_dir(dashboard_dir):
    original = os.getcwd()
    os.chdir(dashboard_dir)
    yield original
    os.chdir(original)


@pytest.mark.parametrize(
    "filename",
    [
        "pages/compare_securities.py",
        "pages/load_portfolio.py",
        "pages/equilibrium_buy.py",
    ],
)
def test_page_loads(original_dir, filename):
    # Initialize the app test with the main app
    at = AppTest.from_file("app.py").run(timeout=30)

    # Try to switch to the page
    at.switch_page(filename)
    at.run()

    # Check if there were any exceptions
    assert not at.exception, (
        f"Exception occurred while loading {filename}: {at.exception}"
    )
