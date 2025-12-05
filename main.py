import logging
from foliotrack.Portfolio import Portfolio
from foliotrack.Equilibrate import solve_equilibrium
from foliotrack.Backtest import run_backtest

logging.basicConfig(level=logging.INFO)


def portfolio_from_scratch():
    # Create a Portfolio instance
    portfolio = Portfolio("Example Portfolio", currency="EUR")

    # Buy some securities
    portfolio.buy_security("AIR.PA", volume=20.0, price=200.0, fill=True)
    portfolio.buy_security("NVDA", volume=1.0, price=600.0, fill=True)
    portfolio.buy_security("MC.PA", volume=1.0, price=300.0, fill=True)

    # Sell some of them
    portfolio.sell_security("AIR.PA", 3.0)

    # Set target shares
    portfolio.set_target_share("AIR.PA", 0.5)
    portfolio.set_target_share("NVDA", 0.2)
    portfolio.set_target_share("MC.PA", 0.3)

    # Run backtest
    result = run_backtest(portfolio, start_date="2010-01-01", end_date="2023-01-01")
    result.display()

    # Save in JSON file
    portfolio.to_json("Portfolios/investment_example.json")

    # Solve for equilibrium
    solve_equilibrium(portfolio, investment_amount=2000.0, min_percent_to_invest=0.99)

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

    portfolio.buy_security("NVDA", volume=100.0, price=300.0)

    # Solve for equilibrium
    solve_equilibrium(
        portfolio, investment_amount=10000.0, min_percent_to_invest=0.99, selling=True
    )

    # Buy additional securities
    portfolio.sell_security("AIR.PA", volume=17.0)
    portfolio.buy_security("NVDA", volume=1.0, price=300.0)
    portfolio.buy_security("MC.PA", volume=2.0, price=200.0)

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
    # use_existing_portfolio()
