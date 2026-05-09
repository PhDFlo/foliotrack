# Paths — resolve Portfolios/ relative to the project root (the folder containing pyproject.toml)
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
PORTFOLIOS_DIR = PROJECT_ROOT / "Portfolios"

# Defaults
DEFAULT_PORTFOLIO_FILE = "investment_example.json"
DEFAULT_CURRENCY = "EUR"
