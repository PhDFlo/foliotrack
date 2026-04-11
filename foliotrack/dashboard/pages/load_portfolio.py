import streamlit as st
from foliotrack.domain.Portfolio import Portfolio
from foliotrack.dashboard.utils.sidebar import render_sidebar
from foliotrack.dashboard.utils.portfolio_actions import render_portfolio_actions
from foliotrack.dashboard.utils.formatting import portfolio_to_df
from foliotrack.services.MarketService import MarketService

# Ensure session state
if "portfolio" not in st.session_state:
    st.session_state.portfolio = Portfolio()

st.title("📂 Portfolio Management")

# Side bar for file operations
file_list = render_sidebar()

# List of tickers
ticker_list = list(st.session_state.portfolio.securities.keys())
# List of tickers for buy and sell
ticker_options = [""] + ticker_list

LOAD_DATA_CONFIG = {
    "Name": st.column_config.TextColumn("Name", width="large"),
    "Ticker": st.column_config.TextColumn("Ticker", width="small"),
    "Currency": st.column_config.TextColumn("Currency", width="small"),
    "Price": st.column_config.NumberColumn("Price", format="%.4f"),
    "Actual Share": st.column_config.NumberColumn("Actual Share", format="%.4f"),
    "Target Share": st.column_config.NumberColumn("Target Share", format="%.4f"),
    "Total": st.column_config.NumberColumn("Total value", format=None),
    "Volume": st.column_config.NumberColumn("Volume", format="%.0f"),
}

with st.container(border=True):
    st.subheader("Holdings")

    # Portfolio table block (inlined)
    if "portfolio" not in st.session_state:
        st.error("No portfolio loaded.")
    else:
        df = portfolio_to_df(st.session_state.portfolio)
        st.data_editor(
            df,
            num_rows="dynamic",
            width="stretch",
            column_config=LOAD_DATA_CONFIG,
            key="portfolio_editor",
        )

        if st.button(
            "💰 Update Securities Price", key="update_securities_price", width="stretch"
        ):
            try:
                with st.spinner("Updating prices..."):
                    market_service = MarketService()
                    market_service.update_prices(st.session_state.portfolio)
                st.success("Security prices updated!")
                st.rerun()
            except Exception as e:
                st.error(f"Error updating prices: {str(e)}")

st.divider()

with st.container(border=True):
    st.subheader("Manage Portfolio")
    # Render Actions
    render_portfolio_actions(ticker_options, file_list)
