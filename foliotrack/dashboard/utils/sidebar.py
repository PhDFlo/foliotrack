import streamlit as st
from foliotrack.storage.PortfolioRepository import PortfolioRepository
from foliotrack.dashboard.utils.config import PORTFOLIOS_DIR
from foliotrack.dashboard.utils.file_helpers import get_portfolio_filenames

repo = PortfolioRepository()


def render_sidebar(key="portfolio_file_select") -> list:
    """Sidebar for file operations. Returns list of files."""
    with st.sidebar:
        st.header("Portfolio Files")

        # File selection
        portfolio_files = get_portfolio_filenames()
        # Add empty option
        file_list = [""] + portfolio_files

        selected_file = _selectbox_file(file_list, key)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Refresh", key="refresh"):
                st.rerun()

        with col2:
            if st.button("📂 Load", key="load") and selected_file:
                st.session_state.portfolio = repo.load_from_json(
                    PORTFOLIOS_DIR / selected_file
                )
                st.rerun()

    return file_list


@st.fragment
def _selectbox_file(file_list, key) -> str:
    return st.selectbox(
        "Select Portfolio JSON",
        options=file_list,
        key=key,
        index=1 if len(file_list) > 1 and "investment_example.json" in file_list else 0,
        accept_new_options=True,
    )
