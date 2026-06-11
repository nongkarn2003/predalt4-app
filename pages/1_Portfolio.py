import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.title("📊 Portfolio Analytics")

tickers = st.text_input(
    "Tickers",
    "VT,JQUA,BOND,GLDM,IMOM"
)

tickers = [
    x.strip()
    for x in tickers.split(",")
]

data = yf.download(
    tickers,
    start="2020-01-01",
    auto_adjust=True,
    progress=False
)

prices = data["Close"]

returns = prices.pct_change().dropna()

portfolio = returns.mean(axis=1)

ann_return = (
    (1 + portfolio).prod()
    ** (252 / len(portfolio))
    - 1
)

ann_vol = portfolio.std() * np.sqrt(252)

sharpe = ann_return / ann_vol

st.metric(
    "Annual Return",
    f"{ann_return:.2%}"
)

st.metric(
    "Volatility",
    f"{ann_vol:.2%}"
)

st.metric(
    "Sharpe",
    f"{sharpe:.2f}"
)

st.line_chart(
    (1 + portfolio).cumprod()
)
