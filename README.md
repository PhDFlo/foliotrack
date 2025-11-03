<p align="center">
  <img src="images/logo.jpg" alt="foliotrack Logo" width="80%">
</p>

foliotrack is a Python package to manage, optimize and rebalance securities, including Exchange-Traded Funds (ETFs). Given a set of securities and their target allocation weights, the packages methods compute the optimal investment adjustments required to align the portfolio with the desired strategy.

## Key Features

- **Portfolio Management**:
  - Create, load, and save portfolios in JSON format
  - Track multiple securities across different currencies
  - Automatic price updates from Yahoo Finance
  - Real-time currency conversion using ECB data
  - Buy and sell securities with automatic value adjustments
  - Track target, actual, and final allocation shares

- **Mathematical Optimization**:
  - Mixed-Integer Quadratic Programming (MIQP) for automatic rebalancing towards target allocations
  - Investment constraints (e.g., minimum investment percentage)
  - Solver integration with [CVXPY](https://www.cvxpy.org/) and [PySCIPOpt](https://github.com/scipopt/PySCIPOpt)

- **Multi-Currency Support**:
  - Real-time exchange rates from European Central Bank
  - Automatic currency conversion for portfolio valuation
  - Support for 150+ global currencies
  - Currency symbol and name resolution

- **Real-Time Data Integration**:
  - Security prices via [yfinance](https://github.com/ranaroussi/yfinance) API
  - Company information and metadata retrieval
  - Currency conversion via [ecbdata](https://github.com/LucaMingarelli/ecbdata)
  - Automatic price and value updates

## Use Case

Ideal for investors, financial advisors, and algorithmic traders seeking to:

- Automated Rebalancing – Maintains target asset allocations with minimal manual intervention, ensuring alignment with investment strategies.
- Multi-Currency Support – Dynamically adjusts for exchange rate fluctuations, enabling accurate valuation and rebalancing of global portfolios.

## Project Structure

### Core Modules

- `main.py`: Example usage and entry point with portfolio creation and management examples.
- `foliotrack/Currency.py`: Currency management with symbol resolution, exchange rates, and ECB data integration.
- `foliotrack/Security.py`: Security class with real-time price updates, trading operations, and market data integration.
- `foliotrack/Portfolio.py`: Portfolio management with multi-currency support, security tracking, and allocation management.
- `foliotrack/Equilibrate.py`: Portfolio optimization using MIQP for efficient rebalancing.

### Data

- `foliotrack/data/currencies.json`: Database of 150+ currencies with symbols and metadata.
- `Portfolios/`: Directory for storing portfolio JSON files.
  - `investment_example.json`: Example portfolio configuration.

### Tests

- `tests/foliotrack/`: Comprehensive test suite.
  - `test_currency.py`: Currency operations and exchange rate tests.
  - `test_portfolio.py`: Portfolio management and serialization tests.
  - `test_security.py`: Security operations and market data tests.
  - `test_equilibrate.py`: Portfolio optimization tests.

## Installation

Clone the repository from Github:

```bash
git clone git@github.com:PhDFlo/foliotrack.git
```

In the `foliotrack` folder create the python environment using [uv](https://github.com/astral-sh/uv):

```bash
uv sync
source .venv/bin/activate
```

## Usage Examples

foliotrack provides a comprehensive Python API for portfolio management. Here are some common use cases:

```python
import logging
from foliotrack.Security import Security
from foliotrack.Portfolio import Portfolio
from foliotrack.Equilibrate import Equilibrate

logging.basicConfig(level=logging.INFO)

def main():
    portfolio = Portfolio()

    # Buy some seucirties
    portfolio.buy_security("AIR.PA", quantity=20.0, price=200.0, fill=True)
    portfolio.buy_security("NVDA", quantity=1.0, price=600.0, fill=True)
    portfolio.buy_security("MC.PA", quantity=1.0, price=300.0, fill=True)

    # Sell some of them
    portfolio.sell_security("AIR.PA", 3.0)

    # Set target shares
    portfolio.set_target_share("AIR.PA", 0.5)
    portfolio.set_target_share("NVDA", 0.2)
    portfolio.set_target_share("MC.PA", 0.3)

    # Save in JSON file
    portfolio.to_json("Portfolios/investment_example.json")

    # Solve for equilibrium
    solve_equilibrium(portfolio, investment_amount=1000.0, min_percent_to_invest=0.99)

    # Log portfolio info
    info = portfolio.get_portfolio_info()
    logging.info("Portfolio info:")
    for security_info in info:
        logging.info("Security:")
        for k, v in security_info.items():
            logging.info(f"  {k}: {v}")

if __name__ == "__main__":
    main()
```

Which produces the following output:

```
INFO:root:Security 'AIR.PA' added to portfolio with quantity 20.0.
INFO:root:Exchange rate USD → EUR on latest: 0.8655
INFO:root:Security 'NVDA' added to portfolio with quantity 1.0.
INFO:root:Exchange rate USD → EUR on latest: 0.8655
INFO:root:Security 'MC.PA' added to portfolio with quantity 1.0.
INFO:root:Exchange rate USD → EUR on latest: 0.8655
INFO:root:Sold 3.0 units of security 'AIR.PA'. New number held: 17.0.
INFO:root:Exchange rate USD → EUR on latest: 0.8655
INFO:root:Portfolio saved to Portfolios/investment_example.json
INFO:root:Optimisation status: optimal
INFO:root:Number of each Security to buy:
INFO:root:  Airbus SE: 3 units
INFO:root:  NVIDIA Corporation: 2 units
INFO:root:  LVMH Moët Hennessy - Louis Vuitton, Société Européenne: 0 units
INFO:root:Amount to spend and final share of each Security:
INFO:root:  Airbus SE: 640.20€, Final share = 0.7895
INFO:root:  NVIDIA Corporation: 350.52€, Final share = 0.0973
INFO:root:  LVMH Moët Hennessy - Louis Vuitton, Société Européenne: 0.00€, Final share = 0.1132
INFO:root:Total amount to invest: 990.72€
INFO:root:Portfolio info:
INFO:root:Security:
INFO:root:  name: Airbus SE
INFO:root:  ticker: AIR.PA
INFO:root:  currency: EUR
INFO:root:  symbol: €
INFO:root:  exchange_rate: 1.0
INFO:root:  price_in_security_currency: 213.4
INFO:root:  price_in_portfolio_currency: 213.4
INFO:root:  quantity: 17.0
INFO:root:  number_to_buy: 3
INFO:root:  amount_to_invest: 640.2
INFO:root:  value: 3627.8
INFO:root:  fill: True
INFO:root:  target_share: 0.5
INFO:root:  actual_share: 0.8217
INFO:root:  final_share: 0.7895
INFO:root:Security:
INFO:root:  name: NVIDIA Corporation
INFO:root:  ticker: NVDA
INFO:root:  currency: USD
INFO:root:  symbol: $
INFO:root:  exchange_rate: 0.8655
INFO:root:  price_in_security_currency: 202.49
INFO:root:  price_in_portfolio_currency: 175.26
INFO:root:  quantity: 1.0
INFO:root:  number_to_buy: 2
INFO:root:  amount_to_invest: 350.52
INFO:root:  value: 175.26
INFO:root:  fill: True
INFO:root:  target_share: 0.2
INFO:root:  actual_share: 0.0397
INFO:root:  final_share: 0.0973
INFO:root:Security:
INFO:root:  name: LVMH Moët Hennessy - Louis Vuitton, Société Européenne
INFO:root:  ticker: MC.PA
INFO:root:  currency: EUR
INFO:root:  symbol: €
INFO:root:  exchange_rate: 1.0
INFO:root:  price_in_security_currency: 612.1
INFO:root:  price_in_portfolio_currency: 612.1
INFO:root:  quantity: 1.0
INFO:root:  number_to_buy: 0
INFO:root:  amount_to_invest: 0.0
INFO:root:  value: 612.1
INFO:root:  fill: True
INFO:root:  target_share: 0.3
INFO:root:  actual_share: 0.1386
INFO:root:  final_share: 0.1132
```

## Requirements

- Python 3.12+
- numpy - Array operations and mathematical functions
- cvxpy - Convex optimization modeling
- pyscipopt - Mixed-integer programming solver

### Financial Data Integration

- yfinance - Real-time market data
- ecbdata - Currency exchange rates
- pandas - Data manipulation and analysis

### Development and Testing

- pytest - Unit testing
- ruff - Code formatting and linting
- uv - Python package management and virtual environments
