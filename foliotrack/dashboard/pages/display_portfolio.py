import streamlit as st
import pandas as pd
from foliotrack.services.MarketService import MarketService
from foliotrack.services.StatisticsService import StatisticsService
from foliotrack.dashboard.utils.sidebar import render_sidebar
from foliotrack.dashboard.utils.plots import plot_pie_chart, plot_portfolio_evolution

# Initialize services
market_service = MarketService()
statistics_service = StatisticsService(market_service=market_service)

# Title and Metrics
st.title(f"📊 {st.session_state.portfolio.name}")

# Ensure shares and total_invested are fresh
st.session_state.portfolio.recalculate_shares()

# Calculate high-level stats
total_value = st.session_state.portfolio.total_invested
num_securities = len(st.session_state.portfolio.securities)
symbol = st.session_state.portfolio.symbol

# Calculate performance metrics
performance_metrics = statistics_service.compute_statistics(
    portfolio=st.session_state.portfolio
)

# Performance Statistics
with st.container(border=True):
    m_col1, m_col2, m_col3 = st.columns(3)
    with m_col1:
        st.metric(
            "Total Portfolio Value",
            f"{total_value:,.2f} {symbol}",
            delta=f"{performance_metrics['Last Month Delta']:,.2%} (Compared to Last Month)",
            border=True,
        )
    with m_col2:
        st.metric(
            "Cumulative Annualized Growth Rate (CAGR)",
            f"{performance_metrics['CAGR']:,.2%}",
            border=True,
        )
    with m_col3:
        st.metric(
            "Annualized Volatility",
            f"{performance_metrics['Annualized Volatility']:,.2%}",
            border=True,
        )
with st.container(border=True):
    m_col1, m_col2, m_col3 = st.columns(3)
    with m_col1:
        st.metric(
            "Max Drawdown",
            f"{performance_metrics['Max Drawdown']:,.2%}",
            border=True,
        )
    with m_col2:
        st.metric(
            "Annualized Sharpe Ratio",
            f"{performance_metrics['Annualized Sharpe Ratio']:,.2f}",
            border=True,
        )
    with m_col3:
        st.metric("Number of Securities", num_securities, border=True)

# Side bar for file operations
render_sidebar()

with st.sidebar:
    st.divider()
    st.subheader("Chart Settings")
    min_y_exchange = st.number_input(
        "Min Y (Buy/Sell Plot)",
        value=-5,
    )
    max_y_exchange = st.number_input(
        "Max Y (Buy/Sell Plot)",
        value=20,
    )

# List of tickers
ticker_list = list(st.session_state.portfolio.securities.keys())

# Main Display Area
if ticker_list:
    col_candle, col_pie = st.columns([2, 1])

    with col_candle:
        with st.container(border=True):
            # Check if history exists
            if (
                hasattr(st.session_state.portfolio, "history")
                and st.session_state.portfolio.history
            ):
                start_date = min(
                    event["date"] for event in st.session_state.portfolio.history
                )

                # Get historical data for all tickers in portfolio
                with st.spinner("Fetching historical data..."):
                    hist_tickers = market_service.get_historical_data(
                        ticker_list, start_date=start_date
                    )

                if not hist_tickers.empty:
                    plot_portfolio_evolution(
                        portfolio=st.session_state.portfolio,
                        ticker_list=ticker_list,
                        hist_tickers=hist_tickers,
                        Date=pd.DatetimeIndex(hist_tickers.index),
                        min_y_exchange=min_y_exchange,
                        max_y_exchange=max_y_exchange,
                    )
                else:
                    st.info("No historical data available for these tickers.")
            else:
                st.info(
                    "No history available for this portfolio. Add some transactions to see evolution."
                )

    with col_pie:
        with st.container(border=True):
            plot_pie_chart(
                portfolio=st.session_state.portfolio, ticker_list=ticker_list
            )
else:
    st.info(
        "Your portfolio is currently empty. Go to 'Portfolio & Update Prices' to load or add securities."
    )

# Advanced Performance Metrics
st.subheader("Advanced Performance Metrics")
with st.container(border=True):
    a_col1, a_col2, a_col3 = st.columns(3)
    with a_col1:
        st.metric(
            "Annualized Alpha (Overperformance corrected vs S&P 500)",
            f"{performance_metrics['Alpha (Annualized)']:,.2%}",
            border=True,
        )
    with a_col2:
        st.metric(
            "Beta (Volatility vs S&P 500)",
            f"{performance_metrics['Beta']:,.2f}",
            border=True,
        )
    with a_col3:
        st.metric(
            "Calmar Ratio (Annualized Return / Max Drawdown)",
            f"{performance_metrics['Calmar Ratio']:,.2f}",
            border=True,
        )

# Comparison with Benchmarks
st.subheader("Comparison with S&P 500 Benchmark over the same period")
with st.container(border=True):
    b_col1, b_col2, b_col3 = st.columns(3)
    with b_col1:
        st.metric(
            " Benchmark Annualized Return (S&P 500 CAGR)",
            f"{performance_metrics['Benchmark CAGR']:,.2%}",
            delta=f"{performance_metrics['Benchmark CAGR'] - performance_metrics['CAGR']:,.2%} vs Portfolio CAGR",
            border=True,
        )
    with b_col2:
        st.metric(
            "Benchmark Annualized Volatility (S&P 500 Volatility)",
            f"{performance_metrics['Benchmark Annualized Volatility']:,.2%}",
            delta=f"{performance_metrics['Benchmark Annualized Volatility'] - performance_metrics['Annualized Volatility']:,.2%} vs Portfolio Volatility",
            border=True,
        )
    with b_col3:
        st.metric(
            "Benchmark Annualized Sharpe Ratio (S&P 500 Sharpe Ratio)",
            f"{performance_metrics['Benchmark Annualized Sharpe Ratio']:,.2f}",
            delta=f"{performance_metrics['Benchmark Annualized Sharpe Ratio'] - performance_metrics['Annualized Sharpe Ratio']:,.2f} vs Portfolio Sharpe",
            border=True,
        )
