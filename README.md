# python-DCA

A Python module for managing portfolios of Exchange-Traded Funds (ETFs) with Dollar Cost Averaging (DCA) strategies.

## Features

- Define and manage ETF objects with attributes such as name, ticker, currency, price, and fees.
- Build and manage a portfolio of ETFs, including portfolio share and invested amounts.
- Verify if the portfolio shares sum to 1 and get detailed portfolio information.

## Structure

- `DCA/ETF.py`: Defines the `ETF` class for representing individual ETFs.
- `DCA/Portfolio.py`: Defines the `PortfolioETF` class for managing a portfolio of ETFs.

## Example Usage

```python
from DCA.ETF import ETF
from DCA.Portfolio import PortfolioETF

# Create ETF instances
etf1 = ETF(name="S&P 500", ticker="SPY", price=400.0, fees=0.09)
etf2 = ETF(name="MSCI World", ticker="URTH", price=120.0, fees=0.20)

# Create a portfolio and add ETFs
portfolio = PortfolioETF()
portfolio.add_etf(etf1, portfolio_share=0.6, amount_invested=1000)
portfolio.add_etf(etf2, portfolio_share=0.4, amount_invested=500)

# Get portfolio info
info = portfolio.get_portfolio_info()
print(info)

# Verify if portfolio shares sum to 1
portfolio.verify_shares_sum()
```

## Requirements

- Python 3.8+

## License

MIT License

## Author

Florian
