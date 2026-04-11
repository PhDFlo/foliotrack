import streamlit as st
import plotly.express as px
import pandas as pd
from datetime import date
from foliotrack.services.MarketService import MarketService
from foliotrack.services.BacktestService import BacktestService
from foliotrack.dashboard.utils.sidebar import render_sidebar

st.title("📊 Backtest Simulation")

# Side bar for file operations
render_sidebar()

with st.sidebar:
    st.divider()
    st.header("Backtest Period")
    begin_date = st.date_input(
        "Start Date",
        value=date(2010, 1, 1),
        key="bt_begin_date",
        format="YYYY-MM-DD",
    )

    end_date = st.date_input(
        "End Date",
        value=date.today(),
        key="bt_end_date",
        format="YYYY-MM-DD",
    )

market_service = MarketService()

st.subheader("Backtest")

if "portfolio" in st.session_state:
    if st.button("🎬 Run backtest", key="optimize_button", width="stretch"):
        try:
            with st.spinner("Running backtest..."):
                backtest_service = BacktestService()
                result = backtest_service.run_backtest(
                    st.session_state.portfolio,
                    market_service,
                    start_date=begin_date,
                    end_date=end_date,
                )

            # --- 1. Equity Curve ---
            st.subheader("📈 Portfolio Evolution")
            equity_curve = result.prices
            df_equity = equity_curve.reset_index()
            df_equity.columns = ["Date", "Portfolio Value"]

            fig_equity = px.line(
                df_equity,
                x="Date",
                y="Portfolio Value",
                title="Portfolio Value Over Time",
                template="plotly_dark",
            )
            st.plotly_chart(fig_equity, use_container_width=True)

            # --- 2. Key Statistics ---
            st.subheader("📊 Key Statistics")
            stats = result.stats
            if isinstance(stats, pd.DataFrame):
                stats = stats.iloc[:, 0]

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Return", f"{stats.get('total_return', 0):.2%}")
            with col2:
                st.metric("CAGR", f"{stats.get('cagr', 0):.2%}")
            with col3:
                st.metric("Max Drawdown", f"{stats.get('max_drawdown', 0):.2%}")
            with col4:
                st.metric("Sharpe Ratio", f"{stats.get('daily_sharpe', 0):.2f}")

            with st.expander("See full statistics"):
                st.dataframe(stats)

            # --- 3. Monthly Returns Histogram ---
            st.subheader("📅 Monthly Returns")
            daily_returns = result.prices.pct_change().dropna()

            if isinstance(daily_returns, pd.DataFrame) and not daily_returns.empty:
                daily_returns = daily_returns.iloc[:, 0]

            m_returns = daily_returns.resample("ME").apply(lambda x: (1 + x).prod() - 1)

            fig_hist = px.histogram(
                x=m_returns,
                nbins=30,
                title="Distribution of Monthly Returns",
                labels={"x": "Monthly Return", "y": "Count"},
                template="plotly_dark",
            )
            fig_hist.add_vline(x=0, line_dash="dash", line_color="white")
            st.plotly_chart(fig_hist, use_container_width=True)

            # --- 4. Security Returns (Bar Chart) ---
            st.subheader("🏢 Security Returns")

            tickers = list(st.session_state.portfolio.securities.keys())
            if tickers:
                hist_data = market_service.get_security_historical_data(
                    tickers, start_date=begin_date
                )
                if not hist_data.empty:
                    # Filter dates
                    df_filtered = hist_data.loc[begin_date:end_date]
                else:
                    df_filtered = pd.DataFrame()

                if isinstance(df_filtered.columns, pd.MultiIndex):
                    close_prices = df_filtered["Close"]
                else:
                    close_prices = (
                        df_filtered["Close"]
                        if "Close" in df_filtered.columns
                        else df_filtered
                    )

                if not close_prices.empty:
                    if isinstance(close_prices, pd.DataFrame):
                        period_returns = (
                            close_prices.iloc[-1] / close_prices.iloc[0]
                        ) - 1
                        df_sec_returns = pd.DataFrame(
                            {
                                "Security": period_returns.index,
                                "Return": period_returns.values,
                            }
                        )
                    else:
                        ret = (close_prices.iloc[-1] / close_prices.iloc[0]) - 1
                        df_sec_returns = pd.DataFrame(
                            {"Security": [tickers[0]], "Return": [ret]}
                        )

                    fig_bar = px.bar(
                        df_sec_returns,
                        x="Security",
                        y="Return",
                        title="Period Return by Security",
                        color="Return",
                        color_continuous_scale=px.colors.diverging.RdYlGn,
                        template="plotly_dark",
                    )
                    st.plotly_chart(fig_bar, use_container_width=True)
                else:
                    st.warning("No price data found for securities.")

        except Exception as e:
            st.error(f"Backtest computation failed: {e}")
