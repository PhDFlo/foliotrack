import pandas as pd
from unittest.mock import MagicMock
from foliotrack.domain.Portfolio import Portfolio
from foliotrack.dashboard.utils.formatting import portfolio_to_df, equilibrium_to_df


def test_portfolio_to_df_empty():
    """
    Tests the `portfolio_to_df` function with an empty portfolio.
    Checks that a DataFrame is still returned containing default zeroed columns.
    """
    mock_portfolio = MagicMock(spec=Portfolio)
    mock_portfolio.get_portfolio_info.return_value = []

    df = portfolio_to_df(mock_portfolio)

    # Assert
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 1
    assert df["Name"].iloc[0] == ""
    assert df["Currency"].iloc[0] == "EUR"
    assert df["Price"].iloc[0] == 0.0


def test_portfolio_to_df_populated():
    """
    Tests the `portfolio_to_df` function with a populated portfolio payload.
    Ensures columns like 'Total value' correctly concatenate symbols, and data correctly translates to pandas format.
    """
    mock_portfolio = MagicMock(spec=Portfolio)
    mock_portfolio.get_portfolio_info.return_value = [
        {
            "name": "Apple Inc",
            "ticker": "AAPL",
            "currency": "USD",
            "price_in_security_currency": 150.0,
            "actual_share": 0.4,
            "target_share": 0.5,
            "value": 1500.0,
            "symbol": "$",
            "volume": 10,
        }
    ]

    df = portfolio_to_df(mock_portfolio)

    # Assert
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 1
    assert df["Name"].iloc[0] == "Apple Inc"
    assert df["Ticker"].iloc[0] == "AAPL"
    assert df["Total value"].iloc[0] == "1500.0$"
    assert df["Volume"].iloc[0] == 10


def test_equilibrium_to_df_empty():
    mock_portfolio = MagicMock(spec=Portfolio)
    mock_portfolio.get_portfolio_info.return_value = []

    df = equilibrium_to_df(mock_portfolio)

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 1
    assert df["Amount to Invest"].iloc[0] == 0.0


def test_equilibrium_to_df_populated():
    mock_portfolio = MagicMock(spec=Portfolio)
    mock_portfolio.get_portfolio_info.return_value = [
        {
            "name": "Microsoft",
            "ticker": "MSFT",
            "currency": "USD",
            "price_in_security_currency": 300.0,
            "target_share": 0.5,
            "actual_share": 0.3,
            "final_share": 0.4,
            "amount_to_invest": 1500.0,
            "volume_to_buy": 5,
        }
    ]

    df = equilibrium_to_df(mock_portfolio)

    assert len(df) == 1
    assert df["Name"].iloc[0] == "Microsoft"
    assert df["Amount to Invest"].iloc[0] == 1500.0
    assert df["Volume to buy"].iloc[0] == 5
