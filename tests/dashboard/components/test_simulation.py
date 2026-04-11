import numpy as np
from foliotrack.dashboard.utils.simulation import (
    simulate_contract,
    compute_after_tax_curve,
)


def test_simulate_contract():
    """
    Tests the base case of contract simulation logic over a span of two years.
    Verifies that zero fees allow purely gross compounding over the period.
    """
    contract = {
        "years": 2,
        "initial": 1000.0,
        "annual_return": 0.10,  # 10%
        "security_fee": 0.0,
        "bank_fee": 0.0,
        "yearly_investment": 0.0,
    }

    values, invested = simulate_contract(contract)

    # Assert invested stays same
    assert invested == 1000.0

    # Check shape: year 0, year 1, year 2
    assert len(values) == 3
    assert values[0] == 1000.0

    # Year 1 = 1000 * 1.10 = 1100
    assert values[1] == 1100.0
    # Year 2 = 1100 * 1.10 = 1210
    assert values[2] == 1210.0


def test_simulate_contract_with_fees_and_investments():
    contract = {
        "years": 1,
        "initial": 1000.0,
        "annual_return": 0.10,
        "security_fee": 0.01,  # 1% drop
        "bank_fee": 0.01,  # 1% drop
        "yearly_investment": 100.0,
    }

    values, invested = simulate_contract(contract)

    # Base = 1000.
    # Return = 1100.
    # Sec fee = 1100 * 0.99 = 1089.
    # Bank fee = 1089 * 0.99 = 1078.11
    # Add yearly = 1078.11 + 100 = 1178.11

    assert invested == 1100.0
    assert np.isclose(values[1], 1178.11)


def test_compute_after_tax_curve():
    # Fake values
    values = np.array([1000.0, 1500.0, 800.0])
    invested = 1000.0  # flat invested
    tax_rate = 0.30

    after_tax = compute_after_tax_curve(values, invested, tax_rate)

    # Year 0: No gains => 1000
    assert after_tax[0] == 1000.0

    # Year 1: Gains = 500 => Tax = 150 => After = 1500 - 150 = 1350
    assert after_tax[1] == 1350.0

    # Year 2: Gains = 0 (Loss) => Tax = 0 => After = 800
    assert after_tax[2] == 800.0
