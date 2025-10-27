import logging
from foliotrack.Security import Security
from foliotrack.Portfolio import Portfolio
from foliotrack.Equilibrate import solve_equilibrium

logging.basicConfig(level=logging.INFO)


def portfolio_from_scratch():
    # Create Security instances (disable remote fetching with fill=False)
    security1 = Security(
        ticker="AMDW",  # Amundi MSCI World UCITS Security
        price_in_security_currency=500.0,
        quantity=20.0,
    )
    security2 = Security(
        ticker="NVDA",  # NVIDIA Corporation
        price_in_security_currency=300.0,
        quantity=1.0,
    )
    security3 = Security(
        ticker="EIMI.L",  # iShares Core MSCI Emerging Markets IMI UCITS Security
        price_in_security_currency=200.0,
        quantity=3.0,
    )

    # Create a Portfolio instance
    portfolio = Portfolio()
    portfolio.add_security(security1)
    portfolio.add_security(security2)
    portfolio.add_security(security3)

    portfolio.set_target_share("AMDW", 0.5)
    portfolio.set_target_share("NVDA", 0.2)
    portfolio.set_target_share("EIMI.L", 0.3)

    portfolio.to_json("Portfolios/investment_example.json")

    portfolio.update_portfolio()

    # Solve for equilibrium
    solve_equilibrium(portfolio, investment_amount=500.0, min_percent_to_invest=0.99)

    # Log portfolio info
    info = portfolio.get_portfolio_info()
    logging.info("Portfolio info:")
    for security_info in info:
        logging.info("Security:")
        for k, v in security_info.items():
            logging.info(f"  {k}: {v}")


def use_existing_portfolio():
    # Load an existing portfolio from CSV
    portfolio = Portfolio.from_json("Portfolios/investment_example.json")
    portfolio.update_portfolio()

    # Solve for equilibrium
    solve_equilibrium(portfolio, investment_amount=1000.0, min_percent_to_invest=0.99)

    # Buy some Securitys
    nvda1 = Security(
        ticker="NVDA",  # NVIDIA Corporation
        price_in_security_currency=300.0,
        quantity=1.0,
    )
    portfolio.buy_security(nvda1)

    eimi5 = Security(
        ticker="EIMI.L",  # iShares Core MSCI Emerging Markets IMI UCITS Security
        price_in_security_currency=200.0,
        quantity=5.0,
    )
    portfolio.buy_security(eimi5)

    # Log portfolio info
    info = portfolio.get_portfolio_info()
    logging.info("Portfolio info after buys:")
    for security_info in info:
        logging.info("Security:")
        for k, v in security_info.items():
            logging.info(f"  {k}: {v}")

    # Export updated portfolio
    portfolio.to_json("Portfolios/portfolio_output.json")


if __name__ == "__main__":
    portfolio_from_scratch()
    use_existing_portfolio()
