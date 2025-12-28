<p align="center">
  <img src="images/logo.jpg" alt="foliotrack Logo" width="80%">
</p>

foliotrack is a Python package to manage, optimize, rebalance, and backtest portfolios of securities, including Exchange-Traded Funds (ETFs). Given a set of securities and their target allocation weights, the package computes the optimal investment adjustments required to align the portfolio with the desired strategy, and can simulate historical performance with backtesting.

## Key Features

- **Portfolio Management**:
  - Create, load, and save portfolios in JSON format
  - Track multiple securities across different currencies
  - Automatic price updates from Yahoo Finance
  - Real-time currency conversion using ECB data
  - Buy and sell securities with automatic value adjustments
  - Track target, actual, and final allocation shares
  - Run portfolio backtest simulations on historical data

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

- **Backtesting**:
  - Simulate historical portfolio performance via [bt](https://github.com/pmorissette/bt)
  - Analyze daily, monthly, yearly, and average returns
  - Risk analysis using metrics like Sharpe ratio

## Use Case

Ideal for investors, financial advisors, and algorithmic traders seeking to:

- **Backtest strategies** – Simulate and analyze historical performance of portfolios and rebalancing strategies.
- **Automated Rebalancing** – Maintain target asset allocations with minimal manual intervention, ensuring alignment with investment strategies.
- **Multi-Currency Support** – Dynamically adjust for exchange rate fluctuations, enabling accurate valuation and rebalancing of global portfolios.

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

foliotrack provides a comprehensive Python API for portfolio management and backtesting. Here is an updated example using the backtest feature:

```python
import logging
from foliotrack.Portfolio import Portfolio
from foliotrack.Equilibrate import solve_equilibrium
from foliotrack.Backtest import run_backtest

logging.basicConfig(level=logging.INFO)

def main():
  # Create a Portfolio instance
  portfolio = Portfolio("Example Portfolio", currency="EUR")

  # Buy some securities
  portfolio.buy_security("AIR.PA", volume=20.0, price=200.0, date="2023-02-14", fill=True)
  portfolio.buy_security("NVDA", volume=1.0, price=600.0, date="2024-05-09", fill=True)
  portfolio.buy_security("MC.PA", volume=1.0, price=300.0, date="2025-08-01", fill=True)

  # Sell some of them
  portfolio.sell_security("AIR.PA", volume=3.0, date="2023-06-01")

  # Set target shares
  portfolio.set_target_share("AIR.PA", 0.5)
  portfolio.set_target_share("NVDA", 0.2)
  portfolio.set_target_share("MC.PA", 0.3)

  # Run backtest (NEW)
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

if __name__ == "__main__":
  main()
```

This produces output including the backtest results and portfolio details, for example:

```
INFO:root:Security 'AIR.PA' added to portfolio with volume 20.0.
INFO:root:Security 'NVDA' added to portfolio with volume 1.0.
INFO:root:Exchange rate USD → EUR on latest: 0.8484
INFO:root:Security 'MC.PA' added to portfolio with volume 1.0.
INFO:root:Exchange rate USD → EUR on latest: 0.8484
INFO:root:Sold 3.0 units of security 'AIR.PA'. New number held: 17.0.
INFO:root:Exchange rate USD → EUR on latest: 0.8484
Stat                 Example Portfolio
-------------------  -------------------
Start                2010-01-03
End                  2022-12-30
Risk-free rate       0.00%

Total Return         1626.31%
Daily Sharpe         0.97
Daily Sortino        1.60
CAGR                 24.52%
Max Drawdown         -48.28%
Calmar Ratio         0.51

MTD                  -4.07%
3m                   21.25%
6m                   16.12%
YTD                  -11.68%
1Y                   -12.01%
3Y (ann.)            14.05%
5Y (ann.)            19.07%
10Y (ann.)           25.32%
Since Incep. (ann.)  24.52%

Daily Sharpe         0.97
Daily Sortino        1.60
Daily Mean (ann.)    25.71%
Daily Vol (ann.)     26.62%
Daily Skew           -0.26
Daily Kurt           5.81
Best Day             10.19%
Worst Day            -13.46%

Monthly Sharpe       1.04
Monthly Sortino      2.02
Monthly Mean (ann.)  25.40%
Monthly Vol (ann.)   24.41%
Monthly Skew         -0.15
Monthly Kurt         1.68
Best Month           27.47%
Worst Month          -25.76%

Yearly Sharpe        1.04
Yearly Sortino       7.05
Yearly Mean          26.74%
Yearly Vol           25.82%
Yearly Skew          -0.18
Yearly Kurt          -1.44
Best Year            65.05%
Worst Year           -11.68%

Avg. Drawdown        -3.67%
Avg. Drawdown Days   24.99
Avg. Up Month        6.01%
Avg. Down Month      -5.17%
Win Year %           75.00%
Win 12m %            86.21%
INFO:root:Exchange rate USD → EUR on latest: 0.8484
INFO:root:Portfolio saved to Portfolios/investment_example.json
INFO:root:Optimisation status: optimal
INFO:root:Number of each Security to buy:
INFO:root:  Airbus SE: 2 units
INFO:root:  NVIDIA Corporation: 6 units
INFO:root:  LVMH Moët Hennessy - Louis Vuitton, Société Européenne: 1 units
INFO:root:Amount to spend and final share of each Security:
INFO:root:  Airbus SE: 391.92€, Final share = 0.6085
INFO:root:  NVIDIA Corporation: 969.90€, Final share = 0.1849
INFO:root:  LVMH Moët Hennessy - Louis Vuitton, Société Européenne: 632.10€, Final share = 0.2066
INFO:root:Total amount to invest: 1993.92€
INFO:root:Portfolio info:
INFO:root:Security:
INFO:root:  name: Airbus SE
INFO:root:  ticker: AIR.PA
INFO:root:  currency: EUR
INFO:root:  symbol: €
INFO:root:  exchange_rate: 1.0
INFO:root:  price_in_security_currency: 195.96
INFO:root:  price_in_portfolio_currency: 195.96
INFO:root:  volume: 17.0
INFO:root:  volume_to_buy: 2
INFO:root:  amount_to_invest: 391.92
INFO:root:  value: 3331.32
INFO:root:  fill: True
INFO:root:  target_share: 0.5
INFO:root:  actual_share: 0.8076
INFO:root:  final_share: 0.6085
...
```

## Requirements

- Python 3.11+
- numpy - Array operations and mathematical functions
- pandas - Data manipulation and analysis
- cvxpy - Convex optimization modeling
- pyscipopt - Mixed-integer programming solver
- yfinance - Real-time market data
- ecbdata - Currency exchange rates
- bt - Backtest computations

### Development and Testing

- pytest - Unit testing
- ruff - Code formatting and linting
- uv - Python package management and virtual environments
