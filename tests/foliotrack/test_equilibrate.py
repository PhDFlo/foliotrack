import pytest
from foliotrack.Equilibrate import solve_equilibrium
from foliotrack.Portfolio import Portfolio


def test_solve_equilibrium():
    # Create a portfolio with some securities
    """
    Test solving for equilibrium given a portfolio and an investment amount.
    """
    portfolio = Portfolio(currency="EUR")
    portfolio.buy_security("SEC1", quantity=0.0, price=100.0, fill=False)
    portfolio.buy_security("SEC2", quantity=0.0, price=200.0, fill=False)
    portfolio.set_target_share("SEC1", 0.6)
    portfolio.set_target_share("SEC2", 0.4)

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
