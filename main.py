import logging
import argparse
from foliotrack.domain.Portfolio import Portfolio
from foliotrack.services.MarketService import MarketService
from foliotrack.services.OptimizationService import OptimizationService
from foliotrack.services.BacktestService import BacktestService
from foliotrack.storage.PortfolioRepository import PortfolioRepository

logging.basicConfig(level=logging.INFO)

# Instantiating Services and Repository
# In a larger app, this would be a dependency injection container.
repo = PortfolioRepository()
optimizer = OptimizationService()
backtester = BacktestService()


def portfolio_from_scratch(market_service: MarketService):
    logging.info("--- Creating Portfolio From Scratch ---")
    # Create a Portfolio instance
    portfolio = Portfolio("Example Portfolio", currency="EUR")

    # Buy some securities (Domain logic: adds to state)
    portfolio.buy_security(
        "AIR.PA", volume=20.0, price=200.0, date="2023-02-14", fill=False
    )
    portfolio.buy_security(
        "NVDA", volume=1.0, price=600.0, date="2024-05-09", fill=False
    )
    portfolio.buy_security(
        "MC.PA", volume=1.0, price=300.0, date="2025-08-01", fill=False
    )

    # Fetch data to fill details (Service logic)
    market_service.update_prices(portfolio)

    # Sell some of them
    portfolio.sell_security("AIR.PA", volume=3.0, date="2023-06-01")

    # Set target shares
    portfolio.set_target_share("AIR.PA", 0.5)
    portfolio.set_target_share("NVDA", 0.2)
    portfolio.set_target_share("MC.PA", 0.3)

    # Run backtest
    # Note: Backtest might need data. If BacktestService handles fetching, it's fine.
    try:
        result = backtester.run_backtest(
            portfolio, start_date="2010-01-01", end_date="2023-01-01"
        )
        result.display()
    except Exception as e:
        logging.error(f"Backtest failed: {e}")

    # Save in JSON file
    repo.save_to_json(portfolio, "Portfolios/investment_example.json")

    # Solve for equilibrium
    optimizer.solve_equilibrium(
        portfolio, investment_amount=2000.0, min_percent_to_invest=0.99
    )

    # Log portfolio info
    _log_portfolio_info(portfolio, "Portfolio info from scratch:")


def use_existing_portfolio(
    market_service: MarketService, path: str = "Portfolios/investment_example.json"
):
    logging.info(f"--- Using Existing Portfolio from {path} ---")

    # Load
    portfolio = repo.load_from_json(path)

    # Update Market Data
    market_service.update_prices(portfolio)

    portfolio.buy_security("NVDA", volume=1000.0, price=300.0)

    # Solve for equilibrium
    optimizer.solve_equilibrium(
        portfolio,
        investment_amount=1000.0,
        min_percent_to_invest=0.99,
        max_different_securities=1,
        selling=False,
    )

    # Buy additional securities
    try:
        portfolio.sell_security("AIR.PA", volume=17.0, date="2024-06-11")
    except ValueError as e:
        logging.warning(f"Could not sell AIR.PA: {e}")

    portfolio.buy_security("NVDA", volume=1.0, price=300.0, date="2024-06-12")
    portfolio.buy_security("MC.PA", volume=2.0, price=200.0, date="2024-06-13")

    # Update stats after trades
    portfolio.recalculate_shares()

    # Log portfolio info
    _log_portfolio_info(portfolio, "Portfolio info after trades:")

    # Export updated portfolio
    repo.save_to_json(portfolio, "Portfolios/portfolio_output.json")


def _log_portfolio_info(portfolio, title):
    info = portfolio.get_portfolio_info()
    logging.info(title)
    for security_info in info:
        logging.info("Security:")
        for k, v in security_info.items():
            logging.info(f"  {k}: {v}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="FolioTrack CLI")
    parser.add_argument(
        "--provider",
        type=str,
        default="yfinance",
        help="Market data provider (yfinance or ffn)",
    )
    parser.add_argument(
        "--action",
        type=str,
        default="all",
        choices=["scratch", "existing", "all"],
        help="Action to perform",
    )

    args = parser.parse_args()

    market_service = MarketService(provider=args.provider)

    if args.action in ["scratch", "all"]:
        portfolio_from_scratch(market_service)

    if args.action in ["existing", "all"]:
        use_existing_portfolio(market_service)
