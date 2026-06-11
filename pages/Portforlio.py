import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# ==================================
# PAGE CONFIG
# ==================================

st.set_page_config(
    page_title="Portfolio Analytics Dashboard",
    layout="wide"
)

st.title("📈 Portfolio Analytics Dashboard")

# ==================================
# PORTFOLIO BUILDER
# ==================================

st.header("Portfolio Builder")

portfolio_df = st.data_editor(
    pd.DataFrame({
        "Ticker": ["VT", "JQUA", "IMOM", "GLDM", "BOND"],
        "Weight": [25, 25, 25, 15, 10]
    }),
    num_rows="dynamic",
    use_container_width=True
)

# ==================================
# BENCHMARK BUILDER
# ==================================

st.header("Benchmark Builder")

benchmark_df = st.data_editor(
    pd.DataFrame({
        "Benchmark": ["ACWI", "SPY"]
    }),
    num_rows="dynamic",
    use_container_width=True
)

# ==================================
# SETTINGS
# ==================================

col1, col2, col3 = st.columns(3)

start_date = col1.date_input(
    "Start Date",
    pd.to_datetime("2020-01-01")
)

end_date = col2.date_input(
    "End Date",
    pd.Timestamp.today()
)

rf = col3.number_input(
    "Risk Free Rate",
    value=0.04,
    step=0.01
)

run = st.button(
    "🚀 Run Analysis",
    use_container_width=True
)

# ==================================
# STOP
# ==================================

if not run:
    st.stop()

# ==================================
# INPUT
# ==================================

portfolio_df = portfolio_df.dropna()

tickers = portfolio_df["Ticker"].astype(str).str.upper().tolist()

weights = np.array(
    portfolio_df["Weight"],
    dtype=float
)

if len(tickers) == 0:
    st.error("Please enter tickers")
    st.stop()

if weights.sum() == 0:
    st.error("Weights cannot sum to zero")
    st.stop()

weights = weights / weights.sum()

benchmarks = (
    benchmark_df["Benchmark"]
    .dropna()
    .astype(str)
    .str.upper()
    .tolist()
)

# ==================================
# DOWNLOAD DATA
# ==================================

all_tickers = list(
    set(tickers + benchmarks)
)

with st.spinner("Downloading data..."):

    data = yf.download(
        all_tickers,
        start=start_date,
        end=end_date,
        auto_adjust=True,
        progress=False
    )

# ==================================
# FIX YFINANCE
# ==================================

if isinstance(data.columns, pd.MultiIndex):

    prices = data["Close"]

else:

    prices = data

prices = prices.ffill().dropna()

returns = prices.pct_change().dropna()

# ==================================
# PORTFOLIO RETURNS
# ==================================

portfolio_returns = (
    returns[tickers] * weights
).sum(axis=1)

# ==================================
# FUNCTIONS
# ==================================

def annual_return(r):

    return (
        (1 + r).prod()
        ** (252 / len(r))
        - 1
    )

def annual_vol(r):

    return (
        r.std()
        * np.sqrt(252)
    )

def sharpe_ratio(r):

    vol = annual_vol(r)

    if vol == 0:
        return np.nan

    return (
        annual_return(r) - rf
    ) / vol

def max_drawdown(r):

    wealth = (
        1 + r
    ).cumprod()

    peak = wealth.cummax()

    drawdown = (
        wealth - peak
    ) / peak

    return drawdown.min()

# ==================================
# KPI
# ==================================

st.header("Portfolio Metrics")

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Annual Return",
    f"{annual_return(portfolio_returns):.2%}"
)

c2.metric(
    "Volatility",
    f"{annual_vol(portfolio_returns):.2%}"
)

c3.metric(
    "Sharpe",
    f"{sharpe_ratio(portfolio_returns):.2f}"
)

c4.metric(
    "Max Drawdown",
    f"{max_drawdown(portfolio_returns):.2%}"
)

# ==================================
# CORRELATION
# ==================================

st.header("Correlation Matrix")

corr = returns[tickers].corr()

st.dataframe(
    corr.round(2),
    use_container_width=True
)

# ==================================
# EQUITY CURVE
# ==================================

st.header("Portfolio Growth")

equity_curve = (
    1 + portfolio_returns
).cumprod()

st.line_chart(
    equity_curve
)

# ==================================
# BENCHMARK COMPARISON
# ==================================

st.header("Benchmark Comparison")

comparison = pd.DataFrame()

comparison["Portfolio"] = (
    1 + portfolio_returns
).cumprod()

for bench in benchmarks:

    if bench in returns.columns:

        comparison[bench] = (
            1 + returns[bench]
        ).cumprod()

st.line_chart(
    comparison
)

# ==================================
# HOLDINGS
# ==================================

st.header("Current Holdings")

weights_report = pd.DataFrame({
    "Ticker": tickers,
    "Weight %": weights * 100
})

st.dataframe(
    weights_report.round(2),
    use_container_width=True
)
