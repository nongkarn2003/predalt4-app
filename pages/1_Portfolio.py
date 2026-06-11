import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(
page_title="Portfolio Analytics Dashboard",
layout="wide"
)

st.title("📈 Portfolio Analytics Dashboard")

# ==================================================

# PORTFOLIO BUILDER

# ==================================================

st.header("Portfolio Builder")

portfolio_df = st.data_editor(
pd.DataFrame({
"Ticker": [
"VT",
"JQUA",
"IMOM",
"GLDM",
"BOND"
],
"Weight": [
25,
25,
25,
15,
10
]
}),
num_rows="dynamic",
use_container_width=True
)

# ==================================================

# BENCHMARK BUILDER

# ==================================================

st.header("Benchmarks")

benchmark_df = st.data_editor(
pd.DataFrame({
"Benchmark": [
"ACWI",
"SPY"
]
}),
num_rows="dynamic",
use_container_width=True
)

# ==================================================

# SETTINGS

# ==================================================

col1, col2, col3 = st.columns(3)

with col1:

```
start_date = st.date_input(
    "Start Date",
    pd.to_datetime("2020-01-01")
)
```

with col2:

```
end_date = st.date_input(
    "End Date",
    pd.Timestamp.today()
)
```

with col3:

```
rf = st.number_input(
    "Risk Free Rate",
    value=0.04,
    step=0.01
)
```

# ==================================================

# RUN

# ==================================================

run = st.button(
"🚀 Run Analysis",
use_container_width=True
)

# ==================================================

# STOP

# ==================================================

if not run:
st.stop()

# ==================================================

# INPUT

# ==================================================

portfolio_df = portfolio_df.dropna()

tickers = portfolio_df["Ticker"].tolist()

weights = np.array(
portfolio_df["Weight"]
)

weights = weights / weights.sum()

benchmarks = benchmark_df[
"Benchmark"
].dropna().tolist()

# ==================================================

# DOWNLOAD

# ==================================================

all_tickers = list(
set(
tickers + benchmarks
)
)

data = yf.download(
all_tickers,
start=start_date,
end=end_date,
auto_adjust=True,
progress=False
)

try:

```
prices = data["Close"]
```

except:

```
prices = data.xs(
    "Close",
    axis=1,
    level=0
)
```

prices = prices.ffill().dropna()

returns = prices.pct_change().dropna()

# ==================================================

# PORTFOLIO RETURN

# ==================================================

portfolio_returns = (
returns[tickers] * weights
).sum(axis=1)

# ==================================================

# FUNCTIONS

# ==================================================

def annual_return(r):

```
return (
    (1+r).prod()
    ** (252/len(r))
    - 1
)
```

def annual_vol(r):

```
return (
    r.std()
    * np.sqrt(252)
)
```

def sharpe(r):

```
return (
    annual_return(r)-rf
) / annual_vol(r)
```

def max_drawdown(r):

```
wealth = (
    1+r
).cumprod()

peak = wealth.cummax()

dd = (
    wealth-peak
) / peak

return dd.min()
```

# ==================================================

# KPI

# ==================================================

st.header("Portfolio Metrics")

c1,c2,c3,c4 = st.columns(4)

c1.metric(
"Return",
f"{annual_return(portfolio_returns):.2%}"
)

c2.metric(
"Volatility",
f"{annual_vol(portfolio_returns):.2%}"
)

c3.metric(
"Sharpe",
f"{sharpe(portfolio_returns):.2f}"
)

c4.metric(
"Max Drawdown",
f"{max_drawdown(portfolio_returns):.2%}"
)

# ==================================================

# CORRELATION

# ==================================================

st.header("Correlation")

corr = (
returns[tickers]
.corr()
)

st.dataframe(
corr.round(2),
use_container_width=True
)

# ==================================================

# RETURNS

# ==================================================

st.header("Portfolio Return Series")

equity_curve = (
1+portfolio_returns
).cumprod()

st.line_chart(
equity_curve
)

# ==================================================

# BENCHMARK COMPARISON

# ==================================================

st.header("Benchmark Comparison")

comparison = pd.DataFrame()

comparison["Portfolio"] = (
1+portfolio_returns
).cumprod()

for bench in benchmarks:

```
if bench in returns.columns:

    comparison[bench] = (
        1+returns[bench]
    ).cumprod()
```

st.line_chart(
comparison
)

# ==================================================

# RAW DATA

# ==================================================

st.header("Portfolio Holdings")

holding_report = pd.DataFrame({

```
"Ticker": tickers,

"Weight %":
weights*100
```

})

st.dataframe(
holding_report.round(2),
use_container_width=True
)
