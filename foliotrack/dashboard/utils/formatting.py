import pandas as pd
from foliotrack.domain.Portfolio import Portfolio


def portfolio_to_df(portfolio: Portfolio) -> pd.DataFrame:
    """Convert portfolio info to DataFrame format for display"""
    info = portfolio.get_portfolio_info()
    data = []
    for security in info:
        data.append(
            {
                "Name": security.get("name"),
                "Ticker": security.get("ticker"),
                "Currency": security.get("currency"),
                "Price": security.get("price_in_security_currency"),
                "Actual Share": security.get("actual_share"),
                "Target Share": security.get("target_share"),
                "Total value": f"{security.get('value')}{security.get('symbol')}",
                "Volume": security.get("volume"),
            }
        )

    if not data:
        return pd.DataFrame(
            {
                "Name": [""],
                "Ticker": [""],
                "Currency": ["EUR"],
                "Price": [0.0],
                "Actual Share": [0.0],
                "Target Share": [0.0],
                "Total Value": [""],
                "Volume": [0.0],
            }
        )

    return pd.DataFrame(data)


def equilibrium_to_df(portfolio: Portfolio) -> pd.DataFrame:
    """Convert portfolio info to DataFrame format for display (Equilibrium view)"""
    info = portfolio.get_portfolio_info()
    data = []
    for security in info:
        data.append(
            {
                "Name": security.get("name"),
                "Ticker": security.get("ticker"),
                "Currency": security.get("currency"),
                "Price": security.get("price_in_security_currency"),
                "Target Share": security.get("target_share"),
                "Actual Share": security.get("actual_share"),
                "Final Share": security.get("final_share"),
                "Amount to Invest": security.get("amount_to_invest"),
                "Volume to buy": security.get("volume_to_buy"),
            }
        )

    if not data:
        return pd.DataFrame(
            {
                "Name": [""],
                "Ticker": [""],
                "Currency": ["EUR"],
                "Price": [0.0],
                "Target Share": [0.0],
                "Actual Share": [0.0],
                "Final Share": [0.0],
                "Amount to Invest": [0.0],
                "Volume to buy": [0.0],
            }
        )

    return pd.DataFrame(data)
