import streamlit as st
from foliotrack.services.OptimizationService import OptimizationService
from foliotrack.dashboard.utils.formatting import equilibrium_to_df
from foliotrack.dashboard.utils.portfolio_actions import render_portfolio_actions
from foliotrack.dashboard.utils.file_helpers import get_portfolio_filenames

# Optimization Parameters
st.title("🎯 Portfolio Optimization")

with st.container(border=True):
    st.subheader("Settings")

    col_amount, col_percent, col_max_sec = st.columns(3)
    with col_amount:
        new_investment = st.number_input(
            "Investment Amount",
            key="investment_amount",
            value=500.0,
            min_value=0.0,
            format="%.2f",
            help="Total amount you want to invest in the portfolio.",
        )
    with col_percent:
        min_percent = st.number_input(
            "Min Invest %",
            key="min_percent",
            value=0.99,
            min_value=0.0,
            max_value=1.0,
            format="%.2f",
            help="Minimum percentage of the investment amount to allocate.",
        )
    with col_max_sec:
        max_diff_sec = st.number_input(
            "Max Securities",
            key="max_diff_sec",
            value=3,
            min_value=0,
            max_value=1000,
            format="%i",
            help="Maximum number of different securities to buy.",
        )

    selling = st.toggle(
        "Allow Selling Securities",
        key="allow_selling",
        value=False,
        help="If enabled, the optimizer can suggest selling existing positions to reach equilibrium.",
    )

# List of tickers for buy and sell
if "ticker_options" not in st.session_state:
    if "portfolio" in st.session_state:
        st.session_state.ticker_options = [""] + list(
            st.session_state.portfolio.securities.keys()
        )
    else:
        st.session_state.ticker_options = [""]

# Retrieve file list for saving
file_list = [""] + get_portfolio_filenames()

# Equilibrium View Block

EQ_DATA_CONFIG = {
    "Name": st.column_config.TextColumn("Name"),
    "Ticker": st.column_config.TextColumn("Ticker"),
    "Currency": st.column_config.TextColumn("Currency"),
    "Price": st.column_config.NumberColumn("Price", format="%.4f"),
    "Target Share": st.column_config.NumberColumn("Target Share", format="%.4f"),
    "Actual Share": st.column_config.NumberColumn("Actual Share", format="%.4f"),
    "Final Share": st.column_config.NumberColumn("Final Share", format="%.4f"),
    "Amount to Invest": st.column_config.NumberColumn(
        "Amount to Invest", format="%.2f"
    ),
    "Volume to buy": st.column_config.NumberColumn("Volume to buy", format="%.0f"),
}

if st.button(
    "🎯 Run Portfolio Optimization",
    key="optimize_button",
    width="stretch",
    type="primary",
):
    try:
        # Run optimization
        optimizer = OptimizationService()
        with st.spinner("Optimizing..."):
            _, st.session_state.total_to_invest, _ = optimizer.solve_equilibrium(
                st.session_state.portfolio,
                investment_amount=float(new_investment),
                min_percent_to_invest=float(min_percent),
                max_different_securities=int(max_diff_sec),
                selling=bool(selling),
            )

        st.session_state.optim_ran = True
    except Exception as e:
        st.error(f"Error during optimization: {str(e)}")

equilibrium_df = equilibrium_to_df(st.session_state.portfolio)

if st.session_state.get("optim_ran"):
    st.subheader("Optimization Results")
    with st.container(border=True):
        st.dataframe(
            equilibrium_df,
            width="stretch",
            column_config=EQ_DATA_CONFIG,
        )

        # Display Total to invest if available
        if hasattr(st.session_state, "total_to_invest"):
            st.info(
                f"**Total to Invest:** {st.session_state.total_to_invest:,.2f} {st.session_state.portfolio.symbol}"
            )

st.divider()

# Re-use portfolio actions
render_portfolio_actions(st.session_state.ticker_options, file_list)
