def create_contract_form(
    st,
    key_prefix,
    label="Contract",
    initial=10000.0,
    annual_return=0.06,
    yearly_investment=0.0,
    security_fee=0.005,
    bank_fee=0.005,
    capgains_tax=0.3,
    years=30,
) -> dict:
    """
    Create a contract form in the Streamlit app with default values and labels.
    """
    st.subheader(f"Contract {key_prefix.upper()}")
    label = st.text_input(
        "Label",
        value=f"{label}",
        key=f"label_{key_prefix}",
    )
    initial = st.number_input(
        f"Initial Investment (e.g. {initial}€)",
        value=initial,
        format="%.2f",
        key=f"initial_{key_prefix}",
    )
    annual_return = st.number_input(
        f"Annual Return (e.g. {annual_return} for {annual_return * 100}%)",
        value=annual_return,
        format="%.3f",
        min_value=0.0,
        max_value=1.0,
        key=f"annual_return_{key_prefix}",
    )
    yearly_investment = st.number_input(
        f"Yearly Investment (e.g. {yearly_investment}€) ",
        value=yearly_investment,
        format="%.2f",
        key=f"yearly_investment_{key_prefix}",
    )
    security_fee = st.number_input(
        f"Annual Security Fee (e.g. {security_fee} for {security_fee * 100}%)",
        value=security_fee,
        format="%.3f",
        min_value=0.0,
        max_value=1.0,
        key=f"security_fee_{key_prefix}",
    )
    bank_fee = st.number_input(
        f"Annual Bank Fee (e.g. {bank_fee} for {bank_fee * 100}%)",
        value=bank_fee,
        format="%.3f",
        min_value=0.0,
        max_value=1.0,
        key=f"bank_fee_{key_prefix}",
    )
    capgains_tax = st.number_input(
        f"Capital Gains Tax (e.g. {capgains_tax} for {capgains_tax * 100}%)",
        value=capgains_tax,
        format="%.3f",
        min_value=0.0,
        max_value=1.0,
        key=f"capgains_tax_{key_prefix}",
    )
    contract = {
        "label": label,
        "initial": initial,
        "annual_return": annual_return,
        "yearly_investment": yearly_investment,
        "security_fee": security_fee,
        "bank_fee": bank_fee,
        "capgains_tax": capgains_tax,
        "years": years,
    }
    return contract
