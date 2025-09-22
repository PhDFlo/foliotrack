<p align="center">
  <img src="images/logo_FolioTrack.jpg" alt="FolioTrack Logo" width="80%">
</p>

FolioTrack is a Python package to manage, optimize and rebalance securities, including Exchange-Traded Funds (ETFs). Given a set of securities and their target allocation weights, the packages methods compute the optimal investment adjustments required to align the portfolio with the desired strategy.

## Key Features
- Mathematical Optimization: Uses Mixed-Integer Quadratic Programming (MIQP) to determine the most efficient asset allocation while respecting constraints (e.g., lot sizes, transaction costs).
- Solver Integration: Leverages [CVXPY](https://www.cvxpy.org/) for convex optimization modeling and [PySCIPOpt](https://github.com/scipopt/PySCIPOpt) as the underlying solver.
- Real-Time Data Fetching:
  - Security prices via [yfinance](https://github.com/ranaroussi/yfinance) (Yahoo Finance API).
  - Currency conversion via [ecbdata](https://github.com/LucaMingarelli/ecbdata) (European Central bank data) for multi-currency portfolios.
- Export Compatibility: Generates output in a format compatible with Wealthfolio for seamless portfolio tracking.
- **Security Contract Comparator tool:** Simulate and compare the evolution of multiple securities investment contracts with customizable fees and taxes, and visualize results interactively.

## Use Case
Ideal for investors, financial advisors, and algorithmic traders seeking to:

✅ Automated Rebalancing – Maintains target asset allocations with minimal manual intervention, ensuring alignment with investment strategies.

✅ Multi-Currency Support – Dynamically adjusts for exchange rate fluctuations, enabling accurate valuation and rebalancing of global portfolios.

✅ User-Friendly GUI – Accelerates workflow with an intuitive interface, reducing complexity for faster decision-making and execution.

✅ Wealthfolio Integration – Exports optimized allocations in a compatible format for seamless tracking via [Wealthfolio](https://github.com/afadil/wealthfolio).


## Project Structure

- `main.py`: Example usage and entry point.
- `gradio-app.py`: Gradio interface.
- `FolioTrack/Currency.py`: Defines the `Currency` class to get currencies informations like symbol and exchange rate.
- `FolioTrack/Security.py`: Defines the `Security` class for representing individual securities.
- `FolioTrack/Portfolio.py`: Defines the `Portfolio` class.
- `FolioTrack/Equilibrate.py`: Defines the `Equilibrate` class which contains the portfolio optimization algorithm.
- `Tools/Contract_security_comparator.py`: Interactive command-line tool to compare security investment contracts with fees and capital gains tax.
- `pyproject.toml`: Project metadata and dependencies.

## Installation

Clone the repository from Github
```
git clone git@github.com:PhDFlo/FolioTrack.git
```

In the `FolioTrack` folder create the python environment using [uv](https://github.com/astral-sh/uv):
```
uv sync
source .venv/bin/activate
```

## Gradio interface Usage

To facilitate the use of the FolioTrack tool a Gradio interface is available by running `python gradio-app.py`. The app will be running locally and should display something like:

```
* Running on local URL:  http://127.0.0.1:7860
* To create a public link, set `share=True` in `launch()`.
```

Open the url in any browser.

<p align="center">
  <img src="images/gradio_interface.png" alt="Gradio interface image" width="100%">
</p>

- To create your securities portfolio, add in the `Inputs` directory a .csv based on the `investment.csv` file.
- Refresh the list of available files by clicking on the `Refresh available files` button and select your file.
- Fill the table by clicking on the `Fill Table from CSV` button. This step is optionnal as you may want to fill the table directly on the web page.
- Select the investment amount you want to add to your portfolio and click on the `New Investment Amount (€)` button. Default is 500€.
- Choose the minimum amount to be invested, default is 99%. Ex: with an investment of 500€, at least 495€ will be placed in the portfolio.
- Finally, compute the optimization to get as close as possible to the target share. 

## Python Example Usage

```python
import logging
from FolioTrack.Security import Security
from FolioTrack.Portfolio import Portfolio
from FolioTrack.Equilibrate import Equilibrate

logging.basicConfig(level=logging.INFO)

def main():
    # Create security instances
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
        name="Vanguard S&P 500 UCITS Security",
        ticker="VUSA.AS",
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
        portfolio.securities, investment_amount=1000.0, min_percent_to_invest=0.99
    )

    # Log portfolio info
    info = portfolio.get_portfolio_info()
    logging.info("Portfolio info:")
    for security_info in info:
        logging.info(f"Security:")
        for k, v in security_info.items():
            logging.info(f"  {k}: {v}")

if __name__ == "__main__":
    main()
```

## Python Example Output
```
INFO:root:Security 'Amundi MSCI World UCITS Security' added to portfolio with share 0.5 and number held 20.0.
INFO:root:Security 'NVIDIA Corporation' added to portfolio with share 0.2 and number held 1.0.
INFO:root:Security 'iShares Core MSCI Emerging Markets IMI UCITS Security' added to portfolio with share 0.3 and number held 3.0.
INFO:root:Portfolio shares sum equal to 1. Portfolio is complete.
INFO:root:Portfolio saved to Portfolios/investment_example.json
INFO:root:Portfolio shares sum equal to 1. Portfolio is complete.
INFO:root:Optimisation status: optimal
INFO:root:Number of each Security to buy:
INFO:root:  Amundi MSCI World UCITS Security: 1 units
INFO:root:  NVIDIA Corporation: 1 units
INFO:root:  iShares Core MSCI Emerging Markets IMI UCITS Security: 7 units
INFO:root:Amount to spend and final share of each Security:
INFO:root:  Amundi MSCI World UCITS Security: 45.61€, Final share = 0.5678
INFO:root:  NVIDIA Corporation: 151.75€, Final share = 0.1799
INFO:root:  iShares Core MSCI Emerging Markets IMI UCITS Security: 297.99€, Final share = 0.2523
INFO:root:Total amount to invest: 495.35€
INFO:root:Portfolio info:
INFO:root:Security:
INFO:root:  name: Amundi MSCI World UCITS Security
INFO:root:  ticker: AMDW
INFO:root:  currency: EUR
INFO:root:  symbol: €
INFO:root:  exchange_rate: 1.0
INFO:root:  price_in_security_currency: 45.61
INFO:root:  price_in_portfolio_currency: 45.61
INFO:root:  yearly_charge: 0.2
INFO:root:  number_held: 20.0
INFO:root:  number_to_buy: 1
INFO:root:  amount_to_invest: 45.61
INFO:root:  amount_invested: 912.2
INFO:root:  target_share: 0.5
INFO:root:  actual_share: 0.77
INFO:root:  final_share: 0.5678
INFO:root:Security:
INFO:root:  name: NVIDIA Corporation
INFO:root:  ticker: NVDA
INFO:root:  currency: USD
INFO:root:  symbol: $
INFO:root:  exchange_rate: 0.8533879501621437
INFO:root:  price_in_security_currency: 177.82
INFO:root:  price_in_portfolio_currency: 151.7494452978324
INFO:root:  yearly_charge: 0.1
INFO:root:  number_held: 1.0
INFO:root:  number_to_buy: 1
INFO:root:  amount_to_invest: 151.75
INFO:root:  amount_invested: 151.7494452978324
INFO:root:  target_share: 0.2
INFO:root:  actual_share: 0.13
INFO:root:  final_share: 0.1799
INFO:root:Security:
INFO:root:  name: iShares Core MSCI Emerging Markets IMI UCITS Security
INFO:root:  ticker: EIMI.L
INFO:root:  currency: EUR
INFO:root:  symbol: €
INFO:root:  exchange_rate: 1.0
INFO:root:  price_in_security_currency: 42.57
INFO:root:  price_in_portfolio_currency: 42.57
INFO:root:  yearly_charge: 0.25
INFO:root:  number_held: 3.0
INFO:root:  number_to_buy: 7
INFO:root:  amount_to_invest: 297.99
INFO:root:  amount_invested: 127.71000000000001
INFO:root:  target_share: 0.3
INFO:root:  actual_share: 0.11
INFO:root:  final_share: 0.2523
```

## Tools

### Security Contract Comparator Usage

The `Contract_security_comparator.py` script allows you to simulate and compare the evolution of multiple securities investment contracts, each with its own fees and capital gains tax. You can define any number of contracts directly from the command line. It provides quantitative information to choose the best contract for investing on a particular security.

**Example usage:**
```sh
python Contract_security_comparator.py --initial 20000 --annual-return 0.06 --years 25 --yearly_contribution 1000 \
  --contract "A,0.0059,0.006,0.172" \
  --contract "B,0.0012,0.00,0.30"
```
- `--contract "Label,Security_fee,Bank_fee,CapitalGainsTax"`: Add as many contracts as you want, each with its own parameters.
- All values for fees and taxes are expressed as decimals (e.g., 0.0059 for 0.59%).

The script will print the results for each contract and plot a graph comparing their evolution and final after-tax values.

## Requirements

- Python 3.12+
- numpy
- cvxpy
- pyscipopt
- gradio
- pandas
- matplotlib
- pyQt6
- yfinance
- ecbdata


## License

MIT License