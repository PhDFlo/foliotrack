import gradio as gr
from DCA.ETF import ETF
from DCA.Portfolio import PortfolioETF
import numpy as np

# Helper to build portfolio from user input
def optimize_portfolio(etf_data, new_investment):
    portfolio = PortfolioETF()
    for etf in etf_data:
        etf_obj = ETF(
            name=etf[0],
            ticker=etf[1],
            currency=etf[2],
            price=float(etf[3]),
            fees=float(etf[4])
        )
        portfolio.add_etf(
            etf_obj,
            target_share=float(etf[5]),
            amount_invested=float(etf[6])
        )
    portfolio.compute_actual_shares()
    portfolio.solve_equilibrium(float(new_investment))
    info = portfolio.get_portfolio_info()
    # Format output for Gradio
    result = ""
    for etf_info in info:
        result += "ETF:\n"
        for k, v in etf_info.items():
            result += f"  {k}: {v}\n"
        result += "\n"
    return result

with gr.Blocks() as demo:
    gr.Markdown("# ETF Portfolio Optimizer")
    etf_table = gr.Dataframe(
        headers=["Name", "Ticker", "Currency", "Price", "Fees", "Target Share", "Amount Invested"],
        datatype=["str", "str", "str", "number", "number", "number", "number"],
        row_count=10,  # Increased from 3 to 10
        col_count=7,
        label="ETF List (add or edit rows)"
    )
    new_investment = gr.Number(label="New Investment Amount", value=1000.0)
    output = gr.Textbox(label="Optimized Portfolio Info", lines=15)
    run_btn = gr.Button("Optimize Portfolio")
    run_btn.click(optimize_portfolio, inputs=[etf_table, new_investment], outputs=output)

demo.launch()
