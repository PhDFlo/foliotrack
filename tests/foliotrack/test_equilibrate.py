import pytest
from foliotrack.Equilibrate import solve_equilibrium
from foliotrack.Portfolio import Portfolio
from foliotrack.Security import Security


def test_solve_equilibrium():
    # Create a portfolio with some securities
    """
    Test solving for equilibrium given a portfolio and an investment amount.
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

    # Solve for equilibrium
    security_counts, total_to_invest, final_shares = solve_equilibrium(
        portfolio, investment_amount=1000
    )

    # Check results
    assert security_counts[0] == 6  # 6 units of Security1
    assert security_counts[1] == 2  # 2 units of Security2
    assert total_to_invest == 1000
    assert final_shares[0] == pytest.approx(0.6, 0.01)
    assert final_shares[1] == pytest.approx(0.4, 0.01)
