import gradio as gr
from ETFOptim.ETF import ETF
from ETFOptim.Portfolio import Portfolio
import numpy as np
import pandas as pd
import datetime

# Global portfolio instance (keeps state across tabs)
portfolio = Portfolio()


def update_file_explorer():
    return gr.FileExplorer(root_dir="/")


def update_file_explorer_2():
    return gr.FileExplorer(root_dir="./Portfolios")


def update_table_from_file(inp):
    df = pd.read_csv(inp, delimiter=",")
    df = df.to_numpy()
    portfolio.etfs.clear()
    for row in df:
        etf = ETF(
            name=row[0],
            ticker=row[1],
            currency=row[2],
            price=float(row[3]),
            yearly_charge=float(row[4]),
            target_share=float(row[5]),
            number_held=float(row[7]),
        )
        portfolio.add_etf(etf)
    portfolio.compute_actual_shares()
    return df.tolist()


def save_portfolio_to_csv(filename):
    portfolio.to_csv(filename)
    return f"Portfolio saved to {filename}"


def optimize_portfolio(etf_data, new_investment, min_percent):
    portfolio.etfs.clear()
    for etf in etf_data:
        etf_obj = ETF(
            name=etf[0],
            ticker=etf[1],
            currency=etf[2],
            price=float(etf[3]),
            yearly_charge=float(etf[4]),
            target_share=float(etf[5]),
            number_held=float(etf[7]),
        )
        portfolio.add_etf(etf_obj)
    portfolio.compute_actual_shares()
    from ETFOptim.Equilibrate import Equilibrate
    Equilibrate.solve_equilibrium(
        portfolio.etfs,
        investment_amount=float(new_investment),
        min_percent_to_invest=float(min_percent),
    )
    info = portfolio.get_portfolio_info()
    portfolio_data = []
    for etf_info in info:
        portfolio_data.append(
            {
                "Name": etf_info.get("name"),
                "Ticker": etf_info.get("ticker"),
                "Currency": etf_info.get("currency"),
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
    return (
        pd.DataFrame(
            info,
            columns=[
                "name",
                "ticker",
                "currency",
                "price",
                "yearly_charge",
                "target_share",
                "amount_invested",
                "number_held",
            ],
        )
        .to_numpy()
        .tolist()
    )


# def update_etf_prices():
#    portfolio.update_etf_prices()
#    table_data = []
#    for entry in portfolio.portfolio:
#        # Handle both dict and tuple/list structures
#        if isinstance(entry, dict):
#            etf = entry.get("etf")
#            meta = entry
#        elif isinstance(entry, (tuple, list)) and len(entry) == 2:
#            etf, meta = entry
#        else:
#            continue  # skip malformed entries
#        table_data.append(
#            [
#                etf.name,
#                etf.ticker,
#                etf.currency,
#                etf.price,
#                etf.yearly_charge,
#                meta.get("target_share"),
#                meta.get("amount_invested"),
#                meta.get("number_held"),
#            ]
#        )
#    return pd.DataFrame(
#        table_data,
#        columns=[
#            "Name",
#            "Ticker",
#            "Currency",
#            "Price",
#            "Yearly Charge",
#            "Target Share",
#            "Amount Invested",
#            "Number Held",
#        ],
#    )


def buy_etf(ticker, quantity, buy_price, fee, date):
    try:
        portfolio.buy_etf(ticker, quantity, buy_price=buy_price, date=date, fee=fee)
        return f"Bought {quantity} units of {ticker} at {buy_price}"
    except Exception as e:
        return str(e)


def export_wealthfolio_csv(filename):
    portfolio.purchases_to_wealthfolio_csv(filename)
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
                datatype=[
                    "str",
                    "str",
                    "str",
                    "number",
                    "number",
                    "number",
                    "number",
                    "number",
                ],
                row_count=(10, "dynamic"),
                col_count=8,
                type="numpy",
                label="ETF List (add or edit rows)",
                column_widths=["15%", "5%", "5%", "5%", "5%", "5%", "5%", "5%"],
            )
            with gr.Row():
                with gr.Column():
                    btn_fill = gr.Button("Load CSV Portfolio (optional)")
                    btn_fill.click(
                        update_table_from_file, inputs=inp, outputs=etf_table
                    )
                with gr.Column():
                    btn_update_prices = gr.Button("Update ETF Prices from yfinance")
                    btn_update_prices.click(update_etf_prices, outputs=etf_table)

            # Export Porfolio to CSV
            with gr.Row():
                with gr.Column(scale=1):
                    # Set default filename with today's date in dd_mm_yyyy format
                    default_filename = f"Portfolios/investment_{datetime.datetime.now().strftime('%d_%m_%Y')}.csv"
                    save_filename = gr.Textbox(
                        value=default_filename, label="Save as filename"
                    )
                with gr.Column(scale=1):
                    Text_output = gr.Textbox(label="Output")
            btn_save = gr.Button("Save Portfolio to CSV")
            btn_save.click(
                save_portfolio_to_csv, inputs=save_filename, outputs=Text_output
            )

        with gr.TabItem("Equilibrium, Buy & Export"):

            # New investment amount and minimum percent to invest
            with gr.Row():
                with gr.Column():
                    new_investment = gr.Number(
                        label="New Investment Amount (€)", value=500.0
                    )
                with gr.Column():
                    min_percent = gr.Number(
                        label="Minimum Percentage to Invest", value=0.99
                    )
            equilibrium_table = gr.Dataframe(
                headers=[
                    "Name",
                    "Ticker",
                    "Currency",
                    "Price",
                    "Target Share",
                    "Actual Share",
                    "Final Share",
                    "Amount to Invest",
                    "Number to buy",
                ],
                datatype=[
                    "str",
                    "str",
                    "str",
                    "number",
                    "number",
                    "number",
                    "number",
                    "number",
                    "number",
                ],
                label="Equilibrium Portfolio",
                column_widths=["15%", "5%", "5%", "5%", "5%", "5%", "5%", "5%", "5%"],
            )
            btn_optimize = gr.Button("Optimize Portfolio")
            btn_optimize.click(
                optimize_portfolio,
                inputs=[etf_table, new_investment, min_percent],
                outputs=equilibrium_table,
            )

            # Buy ETFs
            with gr.Row():
                with gr.Column():
                    ticker_list = gr.Textbox(
                        label="ETF Ticker",
                        value="",
                    )
                with gr.Column():
                    quantity = gr.Number(label="Quantity to Buy", value=1.0)
                with gr.Column():
                    date = gr.Textbox(
                        label="Purchase Date yyyy-mm-dd",
                        value=str(datetime.date.today()),
                    )
            with gr.Row():
                with gr.Column():
                    buy_price = gr.Number(label="Buy Price", value=0.0)
                with gr.Column():
                    fee = gr.Number(
                        label="Transaction Fee (in the currency: €, $, ...)",
                        value=0.0,
                    )
                with gr.Column():
                    buy_result = gr.Textbox(label="Buy Result")

            btn_buy = gr.Button("Buy ETF")
            btn_buy.click(
                buy_etf,
                inputs=[ticker_list, quantity, buy_price, fee, date],
                outputs=buy_result,
            )

            # Export staged purchases for Wealthfolio format csv
            with gr.Row():
                with gr.Column():
                    export_filename = gr.Textbox(
                        value="Purchases/staged_purchases.csv",
                        label="Export as filename",
                    )
                with gr.Column():
                    export_result = gr.Textbox(label="Export Result")
            btn_export = gr.Button("Export Staged Purchases")

            btn_export.click(
                export_wealthfolio_csv, inputs=export_filename, outputs=export_result
            )

demo.launch()
