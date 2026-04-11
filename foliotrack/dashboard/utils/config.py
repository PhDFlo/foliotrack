from pathlib import Path
import os

# Paths — resolve Portfolios/ relative to the current working directory
# so users can run `dash` from their project root.
PROJECT_ROOT = Path(os.getcwd())
PORTFOLIOS_DIR = PROJECT_ROOT / "Portfolios"

# Defaults
DEFAULT_PORTFOLIO_FILE = "investment_example.json"
DEFAULT_CURRENCY = "EUR"
