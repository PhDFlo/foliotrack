import logging
from PBalance.Security import Security
from PBalance.Portfolio import Portfolio
from PBalance.Equilibrate import Equilibrate

logging.basicConfig(level=logging.INFO)


def portfolio_from_scratch():
    # Create Security instances
    security1 = Security(
        name="Amundi MSCI World UCITS Security",
        ticker="AMDW",
        currency="EUR",
        price_in_security_currency=500.0,
        yearly_charge=0.2,
        target_share=0.5,
        number_held=20.0,
    )
    security2 = Security(
        name="NVIDIA Corporation",
        ticker="NVDA",
        currency="USD",
        price_in_security_currency=300.0,
        yearly_charge=0.1,
        target_share=0.2,
        number_held=1.0,
    )
    security3 = Security(
        name="iShares Core MSCI Emerging Markets IMI UCITS Security",
        ticker="EIMI.L",
        currency="EUR",
        price_in_security_currency=200.0,
        yearly_charge=0.25,
        target_share=0.3,
        number_held=3.0,
    )

    # Create a Portfolio instance
    portfolio = Portfolio()
    portfolio.add_security(security1)
    portfolio.add_security(security2)
    portfolio.add_security(security3)

    portfolio.to_json("Portfolios/investment_example.json")

    portfolio.update_security_prices()  # Update prices from yfinance
    portfolio.compute_actual_shares()

    # Solve for equilibrium
    Equilibrate.solve_equilibrium(
        portfolio, investment_amount=500.0, min_percent_to_invest=0.99
    )

    # Log portfolio info
    info = portfolio.get_portfolio_info()
    logging.info("Portfolio info:")
    for security_info in info:
        logging.info(f"Security:")
        for k, v in security_info.items():
            logging.info(f"  {k}: {v}")


def use_existing_portfolio():
    # Load an existing portfolio from CSV
    portfolio = Portfolio.from_json("Portfolios/investment_example.json")
    portfolio.update_security_prices()
    portfolio.compute_actual_shares()

    # Solve for equilibrium
    Equilibrate.solve_equilibrium(
        portfolio, investment_amount=1000.0, min_percent_to_invest=0.99
    )

    # Buy some Securitys
    portfolio.buy_security("NVDA", 1.0)
    portfolio.buy_security("EIMI.L", 9.0, buy_price=210.0)

    # Write staged purchases for Wealthfolio import
    portfolio.purchases_to_wealthfolio_csv("Purchases/new_purchases_example.csv")

    # Log portfolio info
    info = portfolio.get_portfolio_info()
    logging.info("Portfolio info:")
    for security_info in info:
        logging.info(f"Security:")
        for k, v in security_info.items():
            logging.info(f"  {k}: {v}")

    # Export updated portfolio to CSV
    portfolio.to_json("Portfolios/portfolio_output.json")


if __name__ == "__main__":
    portfolio_from_scratch()
    use_existing_portfolio()
