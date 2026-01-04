<p align="center">
  <img src="images/logo.jpg" alt="foliotrack Logo" width="50%">
</p>

[![Build](https://github.com/PhDFlo/foliotrack/actions/workflows/python-package.yml/badge.svg)](https://github.com/PhDFlo/foliotrack/actions/workflows/python-package.yml)
[![PyPI Version](https://img.shields.io/pypi/v/foliotrack)](https://pypi.org/project/foliotrack/)
[![PyPI License](https://img.shields.io/pypi/l/foliotrack)](https://pypi.org/project/foliotrack/)

# FolioTrack

**FolioTrack** is a robust, modular Python library for modern portfolio management. It helps you **manage**, **optimize**, **rebalance**, and **backtest** multi-currency investment portfolios with ease.

Designed primarily for **DIY passive investors**, FolioTrack automates the mathematical heavy lifting of maintaining a "lazy" portfolio. It ensures your asset allocation remains perfectly balanced with minimal effort, helping you stick to your long-term strategy without the spreadsheet headaches.

---

## 🚀 Why FolioTrack?

- **🧠 Smart Optimization**: Uses **Mixed-Integer Quadratic Programming (MIQP)** to calculate the best integer number of shares to buy/sell to reach your target allocation, respecting constraints like minimum order size or maximum position count.
- **🌍 Multi-Currency Native**: Seamlessly handles portfolios with assets in different currencies (USD, EUR, GBP, etc.). Real-time exchange rates (ECB) ensure your valuations are always accurate.
- **🏗️ Clean Architecture**: Built with Domain-Driven Design principles. Your core portfolio logic is decoupled from external data providers, making the system testable and extensible.
- **🔌 Pluggable Data**: Comes with support for **yfinance** and **ffn**, but you can easily plug in your own market data provider.
- **📈 Built-in Backtesting**: Validate your strategies against historical data before investing a cent.

## ✨ Features

- **Portfolio Management**
  - Track stocks, ETFs, and other securities.
  - JSON-based persistence for easy saving/loading.
  - Transaction history logging.

- **Advanced Rebalancing**
  - Set target weights (e.g., "60% Stocks, 40% Bonds").
  - Mathematical solver finds the optimal trades to minimize tracking error.
  - **New**: Cardinality constraints (limit number of positions).

- **Data Sources**
  - `yfinance` (Yahoo Finance) support out of the box.
  - `ffn` support for straightforward financial time series.
  - Extensible `MarketService` architecture.

## 🛠️ Installation

FolioTrack uses **[uv](https://github.com/astral-sh/uv)** for fast, reliable dependency management.

```bash
# Clone the repository
git clone git@github.com:PhDFlo/foliotrack.git
cd foliotrack

# Sync dependencies and create virtual env
uv sync

# Activate environment
source .venv/bin/activate
```

## ⚡ Quick Start

### 1. Command Line Interface (CLI)

You can run the included `main.py` entry point to see Foliotrack in action immediately:

```bash
# Create a portfolio from scratch, optimize it, and backtest it
uv run main.py --action scratch

# Use an existing portfolio JSON file
uv run main.py --action existing

# Use a different data provider (if installed)
uv run main.py --provider ffn
```

### 2. Python API

FolioTrack's new modular API is intuitive. Here is a classic "60/40" portfolio example:

```python
from foliotrack.domain.Portfolio import Portfolio
from foliotrack.services.MarketService import MarketService
from foliotrack.services.OptimizationService import OptimizationService
from foliotrack.services.BacktestService import BacktestService
from foliotrack.storage.PortfolioRepository import PortfolioRepository

# 1. Setup Services
market_service = MarketService(provider="yfinance")
optimizer = OptimizationService()
repo = PortfolioRepository()

# 2. Create Portfolio
portfolio = Portfolio("Retirement Fund", currency="EUR")

# Buy classic ETFs (Stocks + Bonds)
portfolio.buy_security("IDDA.AS", volume=50.0) # iShares MSCI World (Stocks)
portfolio.buy_security("AGGH.AS", volume=50.0) # iShares Global Agg Bond (Bonds)

# 3. Enrich with Market Data
market_service.update_prices(portfolio)

# 4. Set Targets (60% Stocks, 40% Bonds) & Optimize
portfolio.set_target_share("IDDA.AS", 0.6)
portfolio.set_target_share("AGGH.AS", 0.4)

# Calculate optimal buys to invest an additional 5000 EUR
optimizer.solve_equilibrium(portfolio, investment_amount=5000.0)

# 5. Save Work
repo.save_to_json(portfolio, "my_portfolio.json")
```

## 🏛️ Architecture

FolioTrack follows a **clean, layered architecture**:

- **`domain/`**: Pure Python data entities (`Portfolio`, `Security`). No external dependencies or I/O here.
- **`services/`**: Business logic and external adapters.
  - `MarketService`: Fetches prices.
  - `OptimizationService`: Runs the solver.
  - `BacktestService`: Runs simulations.
- **`storage/`**: Handles file persistence (`PortfolioRepository`).

This structure ensures that your portfolio data remains safe and stable, regardless of how market APIs or file formats change over time.

## 🤝 Contributing

Contributions are welcome! Please run the test suite before submitting a PR:

```bash
uv run pytest
```

## 📄 License

Apache License 2.0. See `LICENSE` for details.
