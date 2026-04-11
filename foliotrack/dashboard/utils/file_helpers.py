from foliotrack.domain.Portfolio import Portfolio
from foliotrack.storage.PortfolioRepository import PortfolioRepository
from foliotrack.dashboard.utils.config import PORTFOLIOS_DIR


def get_portfolio_files() -> list:
    """Get list of JSON files in Portfolios directory"""
    if not PORTFOLIOS_DIR.exists():
        PORTFOLIOS_DIR.mkdir(parents=True, exist_ok=True)
    return list(PORTFOLIOS_DIR.glob("*.json"))


def get_portfolio_filenames() -> list:
    """Get list of JSON filenames in Portfolios directory"""
    files = get_portfolio_files()
    return [f.name for f in files]


def load_portfolio(filename: str) -> Portfolio:
    """Load portfolio from JSON file"""
    filepath = PORTFOLIOS_DIR / filename
    repo = PortfolioRepository()
    try:
        return repo.load_from_json(str(filepath))
    except Exception as e:
        raise Exception(f"Error loading portfolio {filename}: {str(e)}")


def save_portfolio(portfolio: Portfolio, filename: str) -> str:
    """Save portfolio to JSON file. Returns the full path."""
    repo = PortfolioRepository()
    try:
        PORTFOLIOS_DIR.mkdir(parents=True, exist_ok=True)
        filepath = PORTFOLIOS_DIR / filename
        repo.save_to_json(portfolio, str(filepath))
        return str(filepath)
    except Exception as e:
        raise Exception(f"Error saving portfolio: {str(e)}")
