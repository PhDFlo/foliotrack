from ETFOptim.ETF import ETF
from ETFOptim.Portfolio import PortfolioETF
from ETFOptim.Equilibrate import Equilibrate
import numpy as np


def portfolio_from_scratch():

    # Create an ETF instance
    etf1 = ETF(
        name="Amundi MSCI World UCITS ETF",
        ticker="AMDW",
        currency="EUR",
        price=500.0,
        yearly_charge=0.2,
    )
    etf2 = ETF(
        name="Vanguard S&P 500 UCITS ETF",
        ticker="VUSA.AS",
        currency="USD",
        price=300.0,
        yearly_charge=0.1,
    )
    etf3 = ETF(
        name="iShares Core MSCI Emerging Markets IMI UCITS ETF",
        ticker="EIMI.L",
        currency="EUR",
        price=200.0,
        yearly_charge=0.25,
    )

    # Create a PortfolioETF instance
    securities_account = PortfolioETF()
    securities_account.add_new_etf(etf1, target_share=0.5, number_held=20.0)
    securities_account.add_new_etf(etf2, target_share=0.2, number_held=1.0)
    securities_account.add_new_etf(etf3, target_share=0.3, number_held=3.0)

    securities_account.update_etf_prices()  # Update prices from yfinance

    # Compute the actual share
    securities_account.compute_actual_shares()

    # Solve for equilibrium
    Equilibrate.solve_equilibrium(
        securities_account.portfolio, Investment_amount=1000.0, Min_percent_to_invest=0.99
    )

    # Print portfolio info and its keys/values
    info = securities_account.get_portfolio_info()
    print("\nPortfolio info:")
    for etf_info in info:
        print("ETF:")
        for k, v in etf_info.items():
            print(f"  {k}: {v}")


def use_existing_portfolio():
    # Load an existing portfolio from CSV
    securities_account = PortfolioETF.portfolio_from_csv("Portfolios/investment.csv")

    securities_account.update_etf_prices()

    # Compute the actual share
    securities_account.compute_actual_shares()

    # Solve for equilibrium
    Equilibrate.solve_equilibrium(
        securities_account.portfolio, Investment_amount=1000.0, Min_percent_to_invest=0.99
    )
    
    # Buy some ETFs
    securities_account.buy_etf("VUSA.AS", 1.0) 
    securities_account.buy_etf("EIMI.L", 9.0, buy_price=210.0)  # Assuming a buy price of 210.0
    
    # Write staged purchases for Wealthfolio import
    securities_account.purchases_to_Wealthfolio_csv("Portfolios/staged_purchases.csv")

    # Print portfolio info and its keys/values
    info = securities_account.get_portfolio_info()
    print("\nPortfolio info:")
    for etf_info in info:
        print("ETF:")
        for k, v in etf_info.items():
            print(f"  {k}: {v}")

    # Export updated portfolio to CSV
    securities_account.portfolio_to_csv("Portfolios/portfolio_output.csv")


if __name__ == "__main__":
    use_existing_portfolio()
