import streamlit as st
from foliotrack import get_rate_between, Currency

# Get list of currency codes
c = Currency()
currencies = c._currency_data
currency_codes = [d["name"] + " (" + d["symbol"] + ")" for d in currencies]

st.subheader("Exchange Rates")

st.title("💲 Exchange Rates")

with st.sidebar:
    st.divider()
    st.header("Settings")
    date_str = st.date_input("Date (Historical) — optional", format="YYYY-MM-DD")

with st.container(border=True):
    col1, col2 = st.columns(2)
    with col1:
        from_currency = st.selectbox(
            "From Currency",
            options=currency_codes,
            key="from_currency_select",
            index=currency_codes.index("European Euro (€)")
            if "European Euro (€)" in currency_codes
            else 0,
        )
    with col2:
        to_currency = st.selectbox(
            "To Currency",
            options=currency_codes,
            key="to_currency_select",
            index=currency_codes.index("United States dollar ($)")
            if "United States dollar ($)" in currency_codes
            else 0,
        )
    amount = st.number_input("Amount to Convert", value=1.0, min_value=0.0, format="%f")

st.divider()

# ... (Calculations) ...
from_idx = (
    currency_codes.index(from_currency) if from_currency in currency_codes else None
)
from_currency_code = currencies[from_idx].get("cc")
to_idx = currency_codes.index(to_currency) if to_currency in currency_codes else None
to_currency_code = currencies[to_idx].get("cc")

if st.button("⚖️ Calculate Exchange Rate", width="stretch"):
    if not from_currency or not to_currency:
        st.error("Please provide both from and to currency ISO codes.")
    else:
        try:
            with st.spinner("Fetching rate..."):
                result = get_rate_between(
                    from_currency_code, to_currency_code, date=str(date_str)
                )
        except Exception as e:
            st.error(
                f"Error fetching exchange rate: {e}. Note that reference rates are usually updated at around 16:00 CET by the ECB."
            )
        else:
            st.subheader("Results")
            with st.container(border=True):
                res_col1, res_col2 = st.columns(2)

                if isinstance(result, dict):
                    rate = result.get("rate", 0.0)
                    converted = result.get("converted", 0.0)
                else:
                    rate = float(result)
                    converted = rate * amount

                with res_col1:
                    st.metric(
                        f"Rate ({from_currency_code} → {to_currency_code})",
                        f"{rate:.4f}",
                    )
                with res_col2:
                    st.metric(
                        f"Converted Amount ({to_currency_code})", f"{converted:,.2f}"
                    )

            if isinstance(result, dict):
                with st.expander("See raw response data"):
                    st.write(result)
