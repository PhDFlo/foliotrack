import gradio as gr
from DCA.ETF import ETF
from DCA.Portfolio import PortfolioETF
import numpy as np
import pandas as pd

# Helper to build portfolio from user input
def optimize_portfolio(etf_data, new_investment):
    
    # Create a PortfolioETF instance
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
    # Compute the actual share
    portfolio.compute_actual_shares()
    
    # Solve for equilibrium
    portfolio.solve_equilibrium(float(new_investment))
    info = portfolio.get_portfolio_info()
    
    # Format output for Gradio
    portfolio_data = []
    for etf_info in info:
        portfolio_data.append({
            "Name": etf_info.get("name"), 
            "Price": etf_info.get("price"), 
            "Target Share": etf_info.get("target_share"),
            "Actual Share": etf_info.get("actual_share"),
            "Final Share": etf_info.get("final_share"),
            "Amount to Invest": etf_info.get("amount_to_invest"), 
            "Number to buy": etf_info.get("number_to_buy"),
        })
    
    portfolio_data = pd.DataFrame(portfolio_data)
    return portfolio_data

# Function to update the ETF table from a CSV file
def update_table_from_file(inp):
    # Read initial data from CSV or create an empty DataFrame
    df = pd.read_csv(inp, delimiter=",")
    df = df.to_numpy()  # Convert DataFrame to numpy array for Gradio compatibility
    return df.tolist()

# Function to update file explorer
def update_file_explorer():
    return gr.FileExplorer(root_dir="/")
def update_file_explorer_2():
    return gr.FileExplorer(root_dir="./Inputs")

with gr.Blocks() as demo:
    gr.Markdown("# ETF Portfolio Optimizer")
    
    # File explorer to select CSV files
    inp = gr.FileExplorer(root_dir="./Inputs", 
                value="investment.csv",
                label="CSV Files available", 
                file_count='single')
    
    # Button to refresh file explorer
    btn_refresh = gr.Button("Refresh available files")
    btn_refresh.click(update_file_explorer, outputs=inp).then(update_file_explorer_2, outputs=inp)
    
    # ETF table for user input
    etf_table = gr.Dataframe(
        headers=["Name", "Ticker", "Currency", "Price", "Fees", "Target Share", "Amount Invested"],
        datatype=["str", "str", "str", "number", "number", "number", "number"],
        row_count=(10, 'dynamic'),  
        col_count=7,
        type="numpy",
        label="ETF List (add or edit rows)",
        column_widths=['10%', '5%', '5%', '5%', '5%', '5%', '5%']  # Adjusted widths for better visibility
    )

    # Button to fill table from CSV file
    btn_refresh = gr.Button("Fill Table from CSV (optional)")
    btn_refresh.click(update_table_from_file, inputs=inp, outputs=etf_table)
     
    # Input for new investment amount
    new_investment = gr.Number(label="New Investment Amount (€)", value=500.0)

    # Dataframe to display equilibrium results
    equilibrium_table = gr.Dataframe(
        headers=["Name", "Price", "Target Share", "Actual Share", "Final Share", "Amount to invest", "Number to buy"],
        datatype=["str", "number", "number", "number", "number", "number", "number"],
        label="Equilibrium Portfolio",
        visible=True,
        column_widths=['10%', '5%', '5%', '5%', '5%', '5%', '5%']  # Adjusted widths for better visibility
    )   

    # Button to run optimization
    run_btn = gr.Button("Optimize Portfolio")
    run_btn.click(optimize_portfolio, inputs=[etf_table, new_investment], outputs=equilibrium_table)

demo.launch()
