<p align="center">
  <img src="images/logo.png" alt="ETF-Optimizer Logo" width="50%">
</p>

# ETF-Optimizer


ETF-Optimizer is a Python module for managing portfolios of Exchange-Traded Funds (ETFs) and computing the optimal investment distribution for Dollar Cost Averaging (DCA) strategies. It uses Mixed-Integer Quadratic Programming (MIQP) to optimize your ETF allocations. The convex optimization problem is performed with [CVXPY](https://www.cvxpy.org/) and [PySCIPOpt](https://github.com/scipopt/PySCIPOpt) for the solver.


## Features

- Define and manage ETF objects with attributes such as name, ticker, currency, price, and fees.
- Build a portfolio by specifying target shares and amounts already invested in each ETF.
- Verify that the sum of target shares equals 1 (100%).
- Compute the actual share of each ETF in your portfolio based on invested amounts.
- Solve for the optimal number of each ETF to buy (using cvxpy) to best approach your target allocation given a maximum investment.
- View detailed portfolio information, including target share, actual share, number to buy, and final share after investment.
- Gradio interface to help ETF and portfolio definition
- CSV file read to accelerate use of the interface
- **ETF Contract Comparator:** Simulate and compare the evolution of multiple ETF investment contracts with customizable fees and taxes, and visualize results interactively.


## Project Structure

- `main.py`: Example usage and entry point.
- `gradio-app.py`: Gradio interface.
- `DCA/ETF.py`: Defines the `ETF` class for representing individual ETFs.
- `DCA/Portfolio.py`: Defines the `PortfolioETF` class and optimization logic.
- `compare_etf.py`: Interactive command-line tool to compare ETF investment contracts with fees and capital gains tax.
- `pyproject.toml`: Project metadata and dependencies.

## Installation

Clone the repository from Github
```
git clone git@github.com:PhDFlo/ETF-Optimizer.git
```

In the `ETF-Optimizer` folder create the python environment using [uv](https://github.com/astral-sh/uv):
```
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

## Gradio interface Usage

To facilitate the use of the ETF-Optimizer tool a Gradio interface is available by running `python gradio-app.py`. The app will be running locally and should display something like:

```
* Running on local URL:  http://127.0.0.1:7860
* To create a public link, set `share=True` in `launch()`.
```

Open the url in any browser.

<p align="center">
  <img src="images/gradio_interface.png" alt="ETF-Optimizer Logo" width="100%">
</p>

- To create your ETF portfolio, add in the `Inputs` directory a .csv based on the `investment.csv` file.
- Refresh the list of available files by clicking on the `Refresh available files` button and select your file.
- Fill the table by clicking on the `Fill Table from CSV` button. This step is optionnal as you may want to fill the table directly on the web page.
- Select the investment amount you want to add to your portfolio and click on the `New Investment Amount (€)` button. Default is 500€.
- Choose the minimum amount to be invested, default is 99%. Ex: with an investment of 500€, at least 495€ will be placed in the portfolio.
- Finally, compute the optimization to get as close as possible to the target share. 

## Python Example Usage

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
    portfolio.solve_equilibrium(nvestment_amount=1000.0, Min_percent_to_invest=0.99)

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

## Python Example Output
```
ETF 'Amundi MSCI World UCITS ETF' added to portfolio with share 0.5.
ETF 'Vanguard S&P 500 UCITS ETF' added to portfolio with share 0.2.
ETF 'iShares Core MSCI Emerging Markets IMI UCITS ETF' added to portfolio with share 0.3.

Verifying portfolio shares...
Portfolio shares sum equal to 1. Portfolio is complete.

Optimisation status: optimal

Number of each ETF to buy:
  Amundi MSCI World UCITS ETF: 0
  Vanguard S&P 500 UCITS ETF: 0
  iShares Core MSCI Emerging Markets IMI UCITS ETF: 5

Amount to spend and final share of each ETF:
  Amundi MSCI World UCITS ETF: 0.00€, Final share = 0.4878
  Vanguard S&P 500 UCITS ETF: 0.00€, Final share = 0.1951
  iShares Core MSCI Emerging Markets IMI UCITS ETF: 1000.00€, Final share = 0.3171

Total amount to invest: 1000.00€

Portfolio info:
ETF:
  name: Amundi MSCI World UCITS ETF
  ticker: AMDW
  currency: Euro
  price: 500.0€
  fees: 0.2
  target_share: 0.5
  amount_invested: 2000.0€
  actual_share: 0.65
  number_to_buy: 0
  amount_to_invest: 0.0€
  final_share: 0.4878
ETF:
  name: Vanguard S&P 500 UCITS ETF
  ticker: VUSA
  currency: USD
  price: 300.0€
  fees: 0.1
  target_share: 0.2
  amount_invested: 800.0€
  actual_share: 0.26
  number_to_buy: 0
  amount_to_invest: 0.0€
  final_share: 0.1951
ETF:
  name: iShares Core MSCI Emerging Markets IMI UCITS ETF
  ticker: EIMI
  currency: Euro
  price: 200.0€
  fees: 0.25
  target_share: 0.3
  amount_invested: 300.0€
  actual_share: 0.1
  number_to_buy: 5
  amount_to_invest: 1000.0€
  final_share: 0.3171
```

## ETF Contract Comparator Usage

The `compare_etf.py` script allows you to simulate and compare the evolution of multiple ETF investment contracts, each with its own fees and capital gains tax. You can define any number of contracts directly from the command line. It provides quantitative information to choose the best contract for investing on a particular ETF.

**Example usage:**
```sh
python compare_etf.py --initial 20000 --annual-return 0.06 --years 25 --yearly_contribution 1000 \
  --contract "A,0.0059,0.006,0.172" \
  --contract "B,0.0012,0.00,0.30"
```
- `--contract "Label,ETF_fee,Bank_fee,CapitalGainsTax"`: Add as many contracts as you want, each with its own parameters.
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


## License

MIT License