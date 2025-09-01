import gradio as gr
from ETFOptim.ETF import ETF
from ETFOptim.Portfolio import PortfolioETF
import numpy as np
import pandas as pd
import datetime

# Global portfolio instance (keeps state across tabs)
portfolio = PortfolioETF()

def update_file_explorer():
    return gr.FileExplorer(root_dir="/")

def update_file_explorer_2():
    return gr.FileExplorer(root_dir="./Portfolios")

def update_table_from_file(inp):
    df = pd.read_csv(inp, delimiter=",")
    df = df.to_numpy()
    # Clear portfolio and add ETFs from CSV
    portfolio.portfolio.clear()
    for row in df:
        etf = ETF(
            name=row[0],
            ticker=row[1],
            currency=row[2],
            price=float(row[3]),
            yearly_charge=float(row[4]),
        )
        portfolio.add_new_etf(etf, target_share=float(row[5]), number_held=float(row[7]))
    portfolio.compute_actual_shares()
    return df.tolist()

def save_portfolio_to_csv(filename):
    portfolio.portfolio_to_csv(filename)
    return f"Portfolio saved to {filename}"

def optimize_portfolio(etf_data, new_investment, min_percent):
    # Rebuild portfolio from table
    portfolio.portfolio.clear()
    for etf in etf_data:
        etf_obj = ETF(
            name=etf[0],
            ticker=etf[1],
            currency=etf[2],
            price=float(etf[3]),
            yearly_charge=float(etf[4]),
        )
        portfolio.add_new_etf(etf_obj, target_share=float(etf[5]), number_held=float(etf[7]))
    portfolio.compute_actual_shares()
    # Solve for equilibrium
    from ETFOptim.Equilibrate import Equilibrate
    Equilibrate.solve_equilibrium(
        portfolio.portfolio,
        Investment_amount=float(new_investment),
        Min_percent_to_invest=float(min_percent),
    )
    info = portfolio.get_portfolio_info()
    portfolio_data = []
    for etf_info in info:
        portfolio_data.append(
            {
                "Name": etf_info.get("name"),
                "Price": etf_info.get("price"),
                "Target Share": etf_info.get("target_share"),
                "Actual Share": etf_info.get("actual_share"),
                "Final Share": etf_info.get("final_share"),
                "Amount to Invest": etf_info.get("amount_to_invest"),
                "Number to buy": etf_info.get("number_to_buy"),
            }
        )
    return pd.DataFrame(portfolio_data)

def update_etf_prices():
    portfolio.update_etf_prices()
    info = portfolio.get_portfolio_info()
    return pd.DataFrame(info)

def buy_etf(ticker, quantity, buy_price):
    try:
        portfolio.buy_etf(ticker, quantity, buy_price=buy_price)
        return f"Bought {quantity} units of {ticker} at {buy_price}"
    except Exception as e:
        return str(e)

def export_wealthfolio_csv(filename):
    portfolio.purchases_to_Wealthfolio_csv(filename)
    return f"Staged purchases exported to {filename}"

with gr.Blocks() as demo:
    gr.Markdown("# ETF Portfolio Optimizer")
    with gr.Tabs():
        with gr.TabItem("Portfolio & Update Prices"):
            
            # File explorer to select Portfolio CSV
            inp = gr.FileExplorer(
                root_dir="./Portfolios",
                value="investment.csv",
                label="CSV Files available",
                file_count="single",
            )
            btn_refresh = gr.Button("Refresh available files")
            btn_refresh.click(update_file_explorer, outputs=inp).then(
                update_file_explorer_2, outputs=inp
            )
            
            
            # Show Portfolio
            etf_table = gr.Dataframe(
                headers=[
                    "Name",
                    "Ticker",
                    "Currency",
                    "Price",
                    "Yearly Charge",
                    "Target Share",
                    "Amount Invested",
                    "Number Held",
                ],
                datatype=["str", "str", "str", "number", "number", "number", "number", "number"],
                row_count=(10, "dynamic"),
                col_count=8,
                type="numpy",
                label="ETF List (add or edit rows)",
                column_widths=["10%", "5%", "5%", "5%", "5%", "5%", "5%", "5%"],
            )
            btn_fill = gr.Button("Fill Table from CSV (optional)")
            btn_fill.click(update_table_from_file, inputs=inp, outputs=etf_table)
            
            
            # Update ETF Prices
            prices_table = gr.Dataframe(
                headers=["Name", "Ticker", "Currency", "Price", "Yearly Charge", "Target Share", "Amount Invested", "Number Held"],
                datatype=["str", "str", "str", "number", "number", "number", "number", "number"],
                label="Portfolio with Updated Prices",
                column_widths=["10%", "5%", "5%", "5%", "5%", "5%", "5%", "5%"],
            )
            btn_update_prices = gr.Button("Update ETF Prices from yfinance")
            btn_update_prices.click(update_etf_prices, outputs=prices_table)
            
            
            # Export Porfolio to CSV
            with gr.Row():
                with gr.Column(scale=1):
                    # Set default filename with today's date in dd_mm_yyyy format
                    default_filename = f"Portfolios/investment_{datetime.datetime.now().strftime('%d_%m_%Y')}.csv"
                    save_filename = gr.Textbox(value=default_filename, label="Save as filename")
                with gr.Column(scale=1):
                    Text_output = gr.Textbox(label="Output")
            btn_save = gr.Button("Save Portfolio to CSV")
            btn_save.click(save_portfolio_to_csv, inputs=save_filename, outputs=Text_output)
            

        with gr.TabItem("Equilibrium, Buy & Export"):
            
            # New investment amount and minimum percent to invest
            new_investment = gr.Number(label="New Investment Amount (€)", value=500.0)
            min_percent = gr.Number(label="Minimum Percentage to Invest", value=0.99)
            equilibrium_table = gr.Dataframe(
                headers=["Name", "Price", "Target Share", "Actual Share", "Final Share", "Amount to Invest", "Number to buy"],
                datatype=["str", "number", "number", "number", "number", "number", "number"],
                label="Equilibrium Portfolio",
                column_widths=["10%", "5%", "5%", "5%", "5%", "5%", "5%"],
            )
            btn_optimize = gr.Button("Optimize Portfolio")
            btn_optimize.click(
                optimize_portfolio,
                inputs=[etf_table, new_investment, min_percent],
                outputs=equilibrium_table,)
            
            ticker_list = gr.Dropdown(choices=[], label="ETF Ticker")
            quantity = gr.Number(label="Quantity to Buy", value=1.0)
            buy_price = gr.Number(label="Buy Price", value=0.0)
            btn_buy = gr.Button("Buy ETF")
            buy_result = gr.Textbox(label="Buy Result")
            def update_ticker_choices():
                return [item[1] for item in etf_table.value] if etf_table.value else []
            etf_table.change(update_ticker_choices, outputs=ticker_list)
            btn_buy.click(buy_etf, inputs=[ticker_list, quantity, buy_price], outputs=buy_result)
            export_filename = gr.Textbox(value="Portfolios/staged_purchases.csv", label="Export as filename")
            btn_export = gr.Button("Export Staged Purchases")
            export_result = gr.Textbox(label="Export Result")
            btn_export.click(export_wealthfolio_csv, inputs=export_filename, outputs=export_result)

demo.launch()
