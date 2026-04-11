import streamlit as st
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

from foliotrack.dashboard.utils.simulation import (
    simulate_contract,
    compute_after_tax_curve,
)
from foliotrack.dashboard.utils.contract_form import create_contract_form

plotly_colors = px.colors.qualitative.Plotly

st.title("📚 Security Comparison")

with st.sidebar:
    st.divider()
    st.header("Simulation Settings")
    years = st.number_input("Number of Years", value=30, min_value=1)

contracts = []

col1, col2 = st.columns(2)
with col1:
    with st.container(border=True):
        st.subheader("Contract A")
        contracts.append(
            create_contract_form(
                st,
                "A",
                label="PEA",
                annual_return=0.06,
                capgains_tax=0.172,
                years=years,
            )
        )

with col2:
    with st.container(border=True):
        st.subheader("Contract B")
        contracts.append(
            create_contract_form(
                st,
                "B",
                label="CTO",
                annual_return=0.08,
                capgains_tax=0.30,
                years=years,
            )
        )

st.divider()

if st.button("🚀 Run Comparison", width="stretch"):
    series_list = []
    invested_list = []
    after_tax_curves = []
    labels = []
    for contract in contracts:
        series, invested = simulate_contract(contract)
        after_tax_curve = compute_after_tax_curve(
            series, invested, contract["capgains_tax"]
        )
        series_list.append(series)
        invested_list.append(invested)
        after_tax_curves.append(after_tax_curve)
        labels.append(contract["label"])

    xs = np.arange(0, years + 1)
    fig = go.Figure()
    for idx, (series, after_tax_curve, label) in enumerate(
        zip(series_list, after_tax_curves, labels)
    ):
        fig.add_trace(
            go.Scatter(
                x=xs,
                y=series,
                mode="lines",
                name=f"{label} (Pre-withdrawal)",
                line=dict(color=plotly_colors[idx % len(plotly_colors)], dash="dash"),
            )
        )
        fig.add_trace(
            go.Scatter(
                x=xs,
                y=after_tax_curve,
                mode="lines",
                name=f"{label} (After-tax)",
                line=dict(color=plotly_colors[idx % len(plotly_colors)], dash="solid"),
            )
        )
    fig.update_layout(
        title="Security investment comparison (fees & capital gains tax)",
        xaxis_title="Years",
        yaxis_title="Portfolio value",
        legend_title="Contracts",
        template="plotly_dark",
    )

    # Store results in session state
    st.session_state["comparison_plot"] = fig
    st.session_state["comparison_results"] = {
        "labels": labels,
        "pre_tax": [s[-1] for s in series_list],
        "after_tax": [a[-1] for a in after_tax_curves],
    }

# Results Display
if "comparison_results" in st.session_state:
    results = st.session_state["comparison_results"]
    st.subheader("Final Values (at end of period)")

    with st.container(border=True):
        res_col1, res_col2 = st.columns(2)
        for i, label in enumerate(results["labels"]):
            with [res_col1, res_col2][i % 2]:
                st.write(f"**{label}**")
                st.metric("Final After-Tax", f"{results['after_tax'][i]:,.2f} €")
                st.caption(f"Pre-withdrawal: {results['pre_tax'][i]:,.2f} €")

if "comparison_plot" in st.session_state:
    with st.container(border=True):
        st.plotly_chart(st.session_state["comparison_plot"], use_container_width=True)
