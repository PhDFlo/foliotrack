import os
from pathlib import Path
import pytest
from streamlit.testing.v1.app_test import AppTest


@pytest.fixture
def page_file():
    return "pages/compare_securities.py"


@pytest.fixture
def dashboard_dir():
    return str(Path(__file__).parent.parent.parent.parent / "foliotrack" / "dashboard")


@pytest.fixture
def original_dir(dashboard_dir):
    # Store original directory
    original = os.getcwd()
    # Change to the directory containing app.py for proper path resolution
    os.chdir(dashboard_dir)
    yield original
    # Restore the original directory after test
    os.chdir(original)


def test_edit_contracts(page_file, original_dir):
    """A user increments the number input, then clicks Add"""
    at = AppTest.from_file(page_file).run()

    # Initial A
    for i in range(12):
        at.number_input[i].increment().run()

    # Test assertions
    expected_values = [
        10000.01,
        0.07,
        0.01,
        0.015,
        0.015,
        0.182,
        10000.01,
        0.09,
        0.01,
        0.015,
        0.015,
        0.31,
    ]

    for i, expected in enumerate(expected_values):
        assert at.number_input[i].value == pytest.approx(expected, 0.001)


def test_run_comparison(page_file, original_dir):
    """Run security comparison after incrementing number input"""
    at = AppTest.from_file(page_file).run()
    at.number_input[0].increment().run()
    at.button[0].click().run()

    # Test assertions
    assert at.button[0].value is True

    # Check for labels in markdown (write() uses markdown)
    # The new UI writes **PEA** and **CTO**
    found_labels = [m.value for m in at.markdown]
    assert "**PEA**" in found_labels
    assert "**CTO**" in found_labels

    # Check metrics
    # Metric 0: Final After-Tax for PEA
    # Metric 1: Final After-Tax for CTO
    # (assuming they are in that order)
    # Actually, they are in res_col1 and res_col2.

    # Let's just check the values exist in metrics
    metric_values = [m.value for m in at.metric]
    assert "36,923.97 €" in metric_values
    assert "55,142.94 €" in metric_values
