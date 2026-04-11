import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from foliotrack.domain.Portfolio import Portfolio

COLORS = px.colors.qualitative.Plotly


def plot_pie_chart(portfolio: Portfolio, ticker_list: list[str]):
    if not ticker_list:
        return

    df = pd.DataFrame(columns=("target", "actual", "final"), index=ticker_list)

    for security in portfolio.securities:
        shares = portfolio._get_share(security)
        df.loc[security] = [
            shares.target,
            shares.actual,
            shares.final,
        ]

    # Create subplots: use 'domain' type for Pie subplot
    fig = make_subplots(
        rows=2, cols=1, specs=[[{"type": "domain"}], [{"type": "domain"}]]
    )
    fig.add_trace(
        go.Pie(
            labels=ticker_list,
            values=df.target,
            name="Target",
            marker={"colors": COLORS},
            sort=False,
        ),
        1,
        1,
    )
    fig.add_trace(
        go.Pie(
            labels=ticker_list,
            values=df.actual,
            name="Actual",
            marker={"colors": COLORS},
            sort=False,
        ),
        2,
        1,
    )

    # Use `hole` to create a donut-like pie chart
    fig.update_traces(hole=0.4, hoverinfo="label+percent+name")
    fig.update_layout(
        title_text="Target vs Actual Security Shares",
        height=700,
        # Add annotations in the center of the donut pies.
        annotations=[
            dict(
                text="Target",
                x=0.5,
                y=sum(fig.get_subplot(1, 1).y) / 2,
                font_size=20,
                showarrow=False,
                yanchor="middle",
            ),
            dict(
                text="Actual",
                x=0.5,
                y=sum(fig.get_subplot(2, 1).y) / 2,
                font_size=20,
                showarrow=False,
                yanchor="middle",
            ),
        ],
        showlegend=False,
    )

    st.plotly_chart(fig)


def _get_portfolio_history(
    portfolio: Portfolio,
    ticker_list: list[str],
    hist_tickers: pd.DataFrame,
    Date: pd.DatetimeIndex,
) -> pd.DataFrame:

    # 1. Standardize all indices to naive daily timestamps to avoid match failures (TZ issues, etc.)
    safe_index = pd.to_datetime(Date).tz_localize(None).normalize()
    hist_tickers = hist_tickers.copy()
    hist_tickers.index = (
        pd.to_datetime(hist_tickers.index).tz_localize(None).normalize()
    )

    # 2. Initialize composition dataframe
    portfolio_comp = pd.DataFrame(index=safe_index)
    for t in ticker_list:
        portfolio_comp[f"Volume {t}"] = 0.0
        portfolio_comp[f"Var {t}"] = 0.0

    # 3. Process History: Group by date and ticker to handle multiple events on same day
    history_df = pd.DataFrame(portfolio.history)
    if not history_df.empty:
        history_df["date"] = (
            pd.to_datetime(history_df["date"]).dt.tz_localize(None).dt.normalize()
        )
        history_agg = (
            history_df.groupby(["date", "ticker"])["volume"].sum().reset_index()
        )

        for _, row in history_agg.iterrows():
            ticker = row["ticker"]
            volume = row["volume"]
            event_date = row["date"]

            if ticker not in ticker_list:
                continue

            # Find the nearest valid date in index (>= event_date)
            # searchsorted returns the index where event_date would be inserted to maintain order
            idx = safe_index.searchsorted(event_date)
            if idx < len(safe_index):
                actual_date = safe_index[idx]
                portfolio_comp.at[actual_date, f"Var {ticker}"] += volume

    # 4. Calculate Cumulative volume
    for ticker in ticker_list:
        portfolio_comp[f"Volume {ticker}"] = portfolio_comp[f"Var {ticker}"].cumsum()

    # 5. Compute Total Portfolio Value (OHLC)
    portfolio_comp["Open"] = 0.0
    portfolio_comp["High"] = 0.0
    portfolio_comp["Low"] = 0.0
    portfolio_comp["Close"] = 0.0

    for ticker in ticker_list:
        # Get volume series
        vol = portfolio_comp[f"Volume {ticker}"]

        # Handle MultiIndex OHLC data
        if isinstance(hist_tickers.columns, pd.MultiIndex):
            for ohlc in ["Open", "High", "Low", "Close"]:
                if (ohlc, ticker) in hist_tickers.columns:
                    portfolio_comp[ohlc] += vol * hist_tickers[(ohlc, ticker)]
                elif ("Adj Close", ticker) in hist_tickers.columns:
                    portfolio_comp[ohlc] += vol * hist_tickers[("Adj Close", ticker)]
        # Handle Single Index (simple prices)
        elif ticker in hist_tickers.columns:
            price = hist_tickers[ticker]
            for ohlc in ["Open", "High", "Low", "Close"]:
                portfolio_comp[ohlc] += vol * price

    return portfolio_comp


def plot_portfolio_evolution(
    portfolio: Portfolio,
    ticker_list: list[str],
    hist_tickers: pd.DataFrame,
    Date: pd.DatetimeIndex,
    min_y_exchange: float,
    max_y_exchange: float,
):
    # Get portfolio composition over time
    portfolio_comp = _get_portfolio_history(portfolio, ticker_list, hist_tickers, Date)

    # Create subplot with portfolio value evolution and stacked bar chart of bought/sold volumes
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.25)

    fig.add_trace(
        go.Candlestick(
            x=portfolio_comp.index,
            open=portfolio_comp["Open"],
            high=portfolio_comp["High"],
            low=portfolio_comp["Low"],
            close=portfolio_comp["Close"],
            name="Portfolio value",
        ),
        row=1,
        col=1,
    )

    # Create stacked bar chart of bought and sold volumes over time
    for ticker in ticker_list:
        fig.add_trace(
            go.Bar(
                x=portfolio_comp.index,
                y=portfolio_comp[f"Var {ticker}"],
                name=ticker,
                hoverinfo="x+name+y",
                marker={
                    "color": COLORS[ticker_list.index(ticker) % len(COLORS)],
                    "line": {
                        "width": 3.0,
                        "color": COLORS[ticker_list.index(ticker) % len(COLORS)],
                    },
                },
            ),
            row=2,
            col=1,
        )

    fig.update_layout(
        height=800,
        title_text="Portfolio Time Evolution",
        yaxis_title=f"Portfolio Value ({portfolio.symbol})",
        yaxis2_title="Security Volumes Exchanges, Buy (+) / Sell (-)",
        yaxis=dict(domain=[0.4, 1.0]),
        yaxis2=dict(domain=[0.0, 0.2]),
    )

    # Set y-axis range
    if not portfolio_comp.empty:
        fig["layout"]["yaxis"].update(range=[0, max(portfolio_comp["High"])])
    fig["layout"]["yaxis2"].update(range=[min_y_exchange, max_y_exchange])

    # Display stacked bar chart of security volumes over time
    st.plotly_chart(fig)
