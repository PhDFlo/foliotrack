# DCA-Equilibrium-Tool


DCA-Equilibrium-Tool is a Python module for managing portfolios of Exchange-Traded Funds (ETFs) and computing the optimal investment distribution for Dollar Cost Averaging (DCA) strategies. It uses mathematical optimization to help you reach your target ETF allocations based on your current investments.


## Features

- Define and manage ETF objects with attributes such as name, ticker, currency, price, and fees.
- Build a portfolio by specifying target shares and amounts already invested in each ETF.
- Verify that the sum of target shares equals 1 (100%).
- Compute the actual share of each ETF in your portfolio based on invested amounts.
- Solve for the optimal number of each ETF to buy (using cvxpy) to best approach your target allocation given a maximum investment.
- View detailed portfolio information, including target share, actual share, number to buy, and final share after investment.


## Project Structure

- `main.py`: Example usage and entry point.
- `DCA/ETF.py`: Defines the `ETF` class for representing individual ETFs.
- `DCA/Portfolio.py`: Defines the `PortfolioETF` class and optimization logic.
- `pyproject.toml`: Project metadata and dependencies.


## Example Usage

```python
from DCA.ETF import ETF
from DCA.Portfolio import PortfolioETF

def main():
    # Create ETF instances
    etf1 = ETF(name="Amundi MSCI World UCITS ETF", ticker="AMDW", currency="Euro", price=500.0, fees=0.2)
    etf2 = ETF(name="Vanguard S&P 500 UCITS ETF", ticker="VUSA", currency="USD", price=300.0, fees=0.1)
    etf3 = ETF(name="iShares Core MSCI Emerging Markets IMI UCITS ETF", ticker="EIMI", currency="Euro", price=200.0, fees=0.25)

    # Create a PortfolioETF instance
    portfolio = PortfolioETF()
    portfolio.add_etf(etf1, target_share=0.5, amount_invested=2000.0)
    portfolio.add_etf(etf2, target_share=0.2, amount_invested=800.0)
    portfolio.add_etf(etf3, target_share=0.3, amount_invested=300.0)

    # Compute the actual share
    portfolio.compute_actual_shares()

    # Solve for equilibrium
    portfolio.solve_equilibrium(1000.0)

    # Print portfolio info
    info = portfolio.get_portfolio_info()
    print("\nPortfolio info:")
    for etf_info in info:
        print("ETF:")
        for k, v in etf_info.items():
            print(f"  {k}: {v}")

if __name__ == "__main__":
    main()
```

## Example Output
```
ETF 'Amundi MSCI World UCITS ETF' added to portfolio with share 0.5.
ETF 'Vanguard S&P 500 UCITS ETF' added to portfolio with share 0.2.
ETF 'iShares Core MSCI Emerging Markets IMI UCITS ETF' added to portfolio with share 0.3.
Verifying portfolio shares...
Portfolio shares sum equal to 1. Portfolio is complete.

Optimisation status: optimal

Number of each ETF to buy:
  Amundi MSCI World UCITS ETF: 2
  Vanguard S&P 500 UCITS ETF: 1
  iShares Core MSCI Emerging Markets IMI UCITS ETF: 1

Final share of each ETF:
  Amundi MSCI World UCITS ETF: 0.56
  Vanguard S&P 500 UCITS ETF: 0.22
  iShares Core MSCI Emerging Markets IMI UCITS ETF: 0.22

Total amount to invest: 1200.00€
```

## Installation

Clone the repository and use the code directly, or copy the `DCA` directory into your project. Requires Python 3.12 or higher.


## Requirements

- Python 3.12+
- numpy
- cvxpy
- pyscipopt


## License

MIT License