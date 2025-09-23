import gradio as gr
from foliotrack.Security import Security
from foliotrack.Portfolio import Portfolio
from foliotrack.Equilibrate import solve_equilibrium
import pandas as pd
import datetime

# Global portfolio instance (keeps state across tabs)
portfolio = Portfolio()


def update_file_explorer():
    return gr.FileExplorer(root_dir="/")


def update_file_explorer_2():
    return gr.FileExplorer(root_dir="./Portfolios")


def read_portfolio(filename):
    global portfolio
    portfolio = Portfolio.from_json(filename)
    info = portfolio.get_portfolio_info()
    # Return as list of lists for Gradio table display
    return [
        [
            security.get(key)
            for key in [
                "name",
                "ticker",
                "currency",
                "price_in_security_currency",
                "actual_share",
                "target_share",
                "amount_invested",
                "number_held",
            ]
        ]
        for security in info
    ]


def save_portfolio_to_json(filename):
    portfolio.to_json(filename)
    return f"Portfolio saved to {filename}"


def optimize_portfolio(security_data, new_investment, min_percent):
    portfolio.securities.clear()
    for security in security_data:
        security_obj = Security(
            name=security[0],
            ticker=security[1],
            currency=security[2],
            price_in_security_currency=float(security[3]),
            actual_share=float(security[4]),
            target_share=float(security[5]),
            number_held=float(security[7]),
        )
        portfolio.add_security(security_obj)
    portfolio.compute_actual_shares()

    solve_equilibrium(
        portfolio,
        investment_amount=float(new_investment),
        min_percent_to_invest=float(min_percent),
    )
    info = portfolio.get_portfolio_info()
    portfolio_data = []
    for security_info in info:
        portfolio_data.append(
            {
                "Name": security_info.get("name"),
                "Ticker": security_info.get("ticker"),
                "Currency": security_info.get("currency"),
                "Price": security_info.get("price_in_security_currency"),
                "Target Share": security_info.get("target_share"),
                "Actual Share": security_info.get("actual_share"),
                "Final Share": security_info.get("final_share"),
                "Amount to Invest": security_info.get("amount_to_invest"),
                "Number to buy": security_info.get("number_to_buy"),
            }
        )
    return pd.DataFrame(portfolio_data)


def update_security_prices():
    portfolio.update_security_prices()
    portfolio.compute_actual_shares()
    info = portfolio.get_portfolio_info()
    return (
        pd.DataFrame(
            info,
            columns=[
                "name",
                "ticker",
                "currency",
                "price_in_security_currency",
                "actual_share",
                "target_share",
                "amount_invested",
                "number_held",
            ],
        )
        .to_numpy()
        .tolist()
    )


def buy_security(ticker, quantity, buy_price, fee, date):
    try:
        portfolio.buy_security(
            ticker, quantity, buy_price=buy_price, date=date, fee=fee
        )
        return f"Bought {quantity} unit(s) of {ticker} at {buy_price}"
    except Exception as e:
        return str(e)


def export_wealthfolio_csv(filename):
    portfolio.purchases_to_wealthfolio_csv(filename)
    return f"Staged purchases exported to {filename}"


with gr.Blocks() as demo:
    gr.Markdown("# Security Portfolio Optimizer")
    with gr.Tabs():
        with gr.TabItem("Portfolio & Update Prices"):
            # File explorer to select Portfolio JSON
            inp = gr.FileExplorer(
                root_dir="./Portfolios",
                value="investment_example.json",
                label="JSON Files available",
                file_count="single",
            )
            btn_refresh = gr.Button("Refresh available files")
            btn_refresh.click(update_file_explorer, outputs=inp).then(
                update_file_explorer_2, outputs=inp
            )

            # Show Portfolio
            security_table = gr.Dataframe(
                headers=[
                    "Name",
                    "Ticker",
                    "Currency",
                    "Price",
                    "Actual Share",
                    "Target Share",
                    f"Amount Invested ({portfolio.symbol})",
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
                label="Security List (add or edit rows)",
                column_widths=["15%", "3%", "3%", "3%", "4%", "4%", "5%", "4%"],
            )
            with gr.Row():
                with gr.Column():
                    btn_fill = gr.Button("Load Selected Portfolio (optional)")
                    btn_fill.click(read_portfolio, inputs=inp, outputs=security_table)
                with gr.Column():
                    btn_update_prices = gr.Button("Update Security Prices")
                    btn_update_prices.click(
                        update_security_prices, outputs=security_table
                    )

            # Export Porfolio to JSON
            with gr.Row():
                with gr.Column(scale=1):
                    # Set default filename with today's date in dd_mm_yyyy format
                    default_filename = f"Portfolios/investment_{datetime.datetime.now().strftime('%d_%m_%Y')}.json"
                    save_filename = gr.Textbox(
                        value=default_filename, label="Save as filename"
                    )
                with gr.Column(scale=1):
                    Text_output = gr.Textbox(label="Output")
            btn_save = gr.Button("Save Portfolio")
            btn_save.click(
                save_portfolio_to_json, inputs=save_filename, outputs=Text_output
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
                inputs=[security_table, new_investment, min_percent],
                outputs=equilibrium_table,
            )

            # Buy Securitys
            with gr.Row():
                with gr.Column():
                    ticker_list = gr.Textbox(
                        label="Security Ticker",
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
                    buy_price = gr.Number(label="Unit price", value=0.0)
                with gr.Column():
                    fee = gr.Number(
                        label="Transaction Fee (in the currency: €, $, ...)",
                        value=0.0,
                    )
                with gr.Column():
                    buy_result = gr.Textbox(label="Buy Result")

            btn_buy = gr.Button("Buy Security")
            btn_buy.click(
                buy_security,
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
