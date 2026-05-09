"""Backtest Simulation Page for Foliotrack Dashboard.

This module provides a Streamlit page for running portfolio backtests,
visualizing results including portfolio evolution, statistics, monthly returns,
and individual security performance.
"""

import streamlit as st
import plotly.express as px
import pandas as pd
from datetime import date
from pandas import Timestamp
from foliotrack.services.MarketService import MarketService
from foliotrack.services.BacktestService import BacktestService
from foliotrack.dashboard.utils.sidebar import render_sidebar


def display_key_statistics(stats: pd.Series) -> None:
    """Display key backtest statistics in columns.

    Args:
        stats: Series containing backtest statistics including total_return, cagr,
               max_drawdown, and daily_sharpe values.
    """
    # Display key metrics in four equally-spaced columns
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            "Total Return", value=f"{stats.get('total_return', 0):.2%}", border=True
        )
    with col2:
        st.metric(
            "Compounded Annual Growth Rate",
            value=f"{stats.get('cagr', 0):.2%}",
            border=True,
        )
    with col3:
        st.metric(
            "Max Drawdown", value=f"{stats.get('max_drawdown', 0):.2%}", border=True
        )
    with col4:
        st.metric(
            "Sharpe Ratio", value=f"{stats.get('daily_sharpe', 0):.2f}", border=True
        )

    # Show complete statistics in collapsible expander
    with st.expander("See full statistics"):
        stats_df = stats.to_frame().T if isinstance(stats, pd.Series) else stats
        st.dataframe(stats_df)


def display_monthly_returns_histogram(daily_returns: pd.Series) -> None:
    """Display histogram of monthly returns.

    Compounds daily returns into monthly returns and visualizes their distribution.

    Args:
        daily_returns: Series of daily returns for the portfolio.
    """
    # Compound daily returns into monthly returns (in percentage)
    m_returns = daily_returns.resample("ME").apply(lambda x: ((1 + x).prod() - 1) * 100)

    # Create histogram showing distribution of monthly returns
    fig_hist = px.histogram(
        x=m_returns,
        nbins=30,
        title="Distribution of Monthly Returns",
        labels={"x": "Monthly Return (%)", "y": "Number of Months"},
        template="plotly_dark",
    )
    # Add reference line at zero to highlight positive vs negative months
    fig_hist.add_vline(x=0, line_dash="dash", line_color="white")
    st.plotly_chart(fig_hist, width="stretch")


def display_security_returns(
    market_service: MarketService, portfolio, begin_date: date
) -> None:
    """Display bar chart of security returns.

    Calculates and visualizes the period returns for each security in the portfolio.

    Args:
        market_service: Service for fetching historical price data.
        portfolio: Portfolio object containing securities.
        begin_date: Start date for return calculation.
    """
    # Extract ticker symbols from portfolio
    tickers = list(portfolio.securities.keys())
    if not tickers:
        return

    # Fetch historical price data for all securities
    hist_data = market_service.get_historical_data(tickers, start_date=begin_date)
    if hist_data.empty:
        st.warning("No price data found for securities.")
        return

    # Filter data to match backtest start date
    df_filtered = hist_data.loc[Timestamp(begin_date) :]

    # Extract closing prices from MultiIndex or regular dataframe
    if isinstance(df_filtered.columns, pd.MultiIndex):
        close_prices = df_filtered["Close"]
    else:
        close_prices = (
            df_filtered["Close"] if "Close" in df_filtered.columns else df_filtered
        )

    if close_prices.empty:
        st.warning("No price data found for securities.")
        return

    # Calculate period returns: (end_price / start_price - 1) * 100
    if isinstance(close_prices, pd.DataFrame):
        period_returns = ((close_prices.iloc[-1] / close_prices.iloc[0]) - 1) * 100
        df_sec_returns = pd.DataFrame(
            {
                "Security": period_returns.index,
                "Return (%)": period_returns.values,
            }
        )
    else:
        ret = (close_prices.iloc[-1] / close_prices.iloc[0]) - 1
        df_sec_returns = pd.DataFrame(
            {"Security": [tickers[0]], "Return (%)": [ret * 100]}
        )

    # Create bar chart with color gradient (red for negative, green for positive returns)
    fig_bar = px.bar(
        df_sec_returns,
        x="Security",
        y="Return (%)",
        title="Period Return by Security",
        color="Return (%)",
        color_continuous_scale=px.colors.diverging.RdYlGn,
        template="plotly_dark",
    )
    st.plotly_chart(fig_bar, width="stretch")


# Page title and sidebar setup
st.title("📊 Backtest Simulation")
render_sidebar()

# Sidebar controls for backtest configuration
with st.sidebar:
    st.divider()
    st.header("Backtest Period")
    begin_date = st.date_input(
        "Start Date",
        value=date(2010, 1, 1),
        key="bt_begin_date",
        format="YYYY-MM-DD",
    )

# Initialize service and main section header
market_service = MarketService()
st.subheader("Backtest")

# Check if portfolio is loaded in session state
if "portfolio" in st.session_state:
    # Main backtest execution button
    if st.button("🎬 Run backtest", key="optimize_button", width="stretch"):
        try:
            # Run backtest with progress indicator
            with st.spinner("Running backtest..."):
                backtest_service = BacktestService()
                result = backtest_service.run_backtest(
                    st.session_state.portfolio,
                    market_service,
                    start_date=begin_date,
                )

            # 1. Display portfolio evolution over time

            df_equity = result.prices.reset_index()
            df_equity.columns = ["Date", "Portfolio Value"]

            # Save the start date in a variable for plotting
            backtest_start = df_equity.iloc[0]["Date"]
            st.subheader(
                f"📈 Portfolio Evolution from {backtest_start.strftime('%Y-%m-%d')}"
            )

            fig_equity = px.line(
                df_equity,
                x="Date",
                y="Portfolio Value",
                title="Portfolio Value Over Time",
                template="plotly_dark",
            )
            st.plotly_chart(fig_equity, width="stretch")

            # 2. Display key performance statistics
            st.subheader("📊 Key Statistics")
            stats = result.stats
            if isinstance(stats, pd.DataFrame):
                stats = stats.iloc[:, 0]
            display_key_statistics(stats)

            # 3. Display distribution of monthly returns
            st.subheader("📅 Monthly Returns")
            daily_returns = result.prices.pct_change().dropna()
            if isinstance(daily_returns, pd.DataFrame) and not daily_returns.empty:
                daily_returns = daily_returns.iloc[:, 0]
            display_monthly_returns_histogram(daily_returns)

            # 4. Display individual security performance
            st.subheader("🏢 Security Returns")
            display_security_returns(
                market_service, st.session_state.portfolio, begin_date
            )

        except Exception as e:
            st.error(f"Backtest computation failed: {e}")
