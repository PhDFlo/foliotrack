import streamlit as st
from streamlit_option_menu import option_menu
from foliotrack.domain.Portfolio import Portfolio

# Configure page
st.set_page_config(
    page_title="Portfolio Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize session state for portfolio
if "portfolio" not in st.session_state:
    st.session_state.portfolio = Portfolio()

# Define pages
load_page = st.Page(
    "pages/load_portfolio.py", title="Portfolio & Update Prices", icon="📂"
)
equil_page = st.Page(
    "pages/equilibrium_buy.py", title="Equilibrium, Buy & Export", icon="🎛️"
)
display_page = st.Page(
    "pages/display_portfolio.py", title="Display Portfolio", icon="📺"
)
compare_page = st.Page(
    "pages/compare_securities.py", title="Compare Securities", icon="📚"
)
exchange_page = st.Page("pages/exchange_rates.py", title="Exchange Rates", icon="💲")
backtest_page = st.Page("pages/backtest.py", title="Backtest Simulation", icon="📊")

# Map titles to pages
PAGES_MAP = {
    "Portfolio & Update Prices": load_page,
    "Equilibrium, Buy & Sell": equil_page,
    "Display Portfolio": display_page,
    "Compare Securities": compare_page,
    "Exchange Rates": exchange_page,
    "Backtest Simulation": backtest_page,
}

# Navigation Setup (Hidden default UI)
pg = st.navigation(
    {
        "Manage": [load_page, equil_page, display_page],
        "Tools": [compare_page, exchange_page, backtest_page],
    },
    position="hidden",
)

# Custom Sidebar with option_menu
with st.sidebar:
    st.title("📈 Portfolio Dashboard")
    menu_options = list(PAGES_MAP.keys())

    default_index = 0
    if "selected_page" in st.session_state:
        try:
            default_index = menu_options.index(st.session_state.selected_page)
        except ValueError:
            pass

    selected = option_menu(
        menu_title=None,
        options=menu_options,
        icons=["cloud-upload", "gear", "tv", "book", "currency-exchange", "graph-up"],
        menu_icon="cast",
        default_index=default_index,
        styles={
            "container": {"padding": "0px", "background-color": "transparent"},
            "icon": {"color": "#ff4b4b", "font-size": "18px"},
            "nav-link": {"font-size": "14px", "text-align": "left", "margin": "0px"},
            "nav-link-selected": {"background-color": "#ff4b4b", "color": "white"},
        },
        key="main_menu_nav",
    )

# Switch page only if selection changed
if (
    "selected_page" not in st.session_state
    or selected != st.session_state.selected_page
):
    st.session_state.selected_page = selected
    st.switch_page(PAGES_MAP[selected])

# Run the selected page
pg.run()

# Version footer at the bottom of the main page
st.divider()
st.caption("v0.1.0 - Built with foliotrack")
