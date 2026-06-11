# app.py

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ==========================================

# CONFIG

# ==========================================

st.set_page_config(
page_title="Portfolio Dashboard",
page_icon="📈",
layout="wide"
)

st.title("📈 Portfolio Analytics Dashboard")

# ==========================================

# SIDEBAR INPUT

# ==========================================

st.sidebar.header("Portfolio Builder")

num_assets = st.sidebar.number_input(
"Number of Assets",
min_value=1,
max_value=20,
value=5
)

tickers = []
weights = []

for i in range(num_assets):

```
col1, col2 = st.sidebar.columns(2)

ticker = col1.text_input(
    f"Ticker {i+1}",
    value=""
)

weight = col2.number_input(
    f"Weight {i+1}",
    min_value=0.0,
    value=0.0,
    step=1.0
)

if ticker != "":

    tickers.append(
        ticker.upper()
    )

    weights.append(weight)
```

# ------------------------------------------

num_bench = st.sidebar.number_input(
"Number of Benchmarks",
min_value=1,
max_value=10,
value=3
)

benchmarks = []

for i in range(num_bench):

```
b = st.sidebar.text_input(
    f"Benchmark {i+1}",
    value=""
)

if b != "":

    benchmarks.append(
        b.upper()
    )
```

# ------------------------------------------

start_date = st.sidebar.date_input(
"Start Date",
pd.to_datetime("2020-01-01")
)

end_date = st.sidebar.date_input(
"End Date",
pd.Timestamp.today()
)

rf = st.sidebar.number_input(
"Risk Free Rate",
value=0.04
)

initial_investment = st.sidebar.number_input(
"Initial Investment",
value=100000
)

run_button = st.sidebar.button(
"🚀 Run Analysis"
)

# ==========================================

# STOP IF NOT RUN

# ==========================================

if not run_button:
st.info("Input portfolio and click Run Analysis")
st.stop()

# ==========================================

# VALIDATION

# ==========================================

if len(tickers) == 0:
st.error("Please enter tickers")
st.stop()

weights = np.array(weights)

if weights.sum() == 0:
st.error("Weights cannot be zero")
st.stop()

weights = weights / weights.sum()

# ==========================================

# DOWNLOAD DATA

# ==========================================

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

close = data["Close"]

close = close.ffill().dropna(how="all")

returns = close.pct_change().dropna()

# ==========================================

# PORTFOLIO RETURN

# ==========================================

portfolio_returns = (
returns[tickers] * weights
).sum(axis=1)

# ==========================================

# FUNCTIONS

# ==========================================

def total_return(series):
return (1 + series).prod() - 1

def annual_return(series):
return (
(1 + total_return(series))
** (252 / len(series))
- 1
)

def annual_vol(series):
return (
series.std()
* np.sqrt(252)
)

def sharpe(series, rf):
return (
annual_return(series) - rf
) / annual_vol(series)

def max_drawdown(series):

```
cum = (
    1 + series
).cumprod()

peak = cum.cummax()

dd = (
    cum - peak
) / peak

return dd.min(), dd
```

def var95(series):
return np.percentile(series, 5)

# ==========================================

# METRICS

# ==========================================

mdd, dd_series = max_drawdown(
portfolio_returns
)

metrics = {

```
"Return":
annual_return(
    portfolio_returns
),

"Vol":
annual_vol(
    portfolio_returns
),

"Sharpe":
sharpe(
    portfolio_returns,
    rf
),

"VaR":
var95(
    portfolio_returns
),

"MaxDD":
mdd
```

}

# ==========================================

# KPI

# ==========================================

c1,c2,c3,c4,c5 = st.columns(5)

c1.metric(
"Return",
f"{metrics['Return']:.2%}"
)

c2.metric(
"Volatility",
f"{metrics['Vol']:.2%}"
)

c3.metric(
"Sharpe",
f"{metrics['Sharpe']:.2f}"
)

c4.metric(
"VaR",
f"{metrics['VaR']:.2%}"
)

c5.metric(
"MaxDD",
f"{metrics['MaxDD']:.2%}"
)

# ==========================================

# PORTFOLIO VS BENCHMARK

# ==========================================

st.subheader(
"Portfolio vs Benchmark"
)

fig = go.Figure()

portfolio_curve = (
1 + portfolio_returns
).cumprod()

fig.add_trace(

```
go.Scatter(
    x=portfolio_curve.index,
    y=portfolio_curve,
    name="Portfolio"
)
```

)

for bench in benchmarks:

```
if bench in returns.columns:

    bench_curve = (
        1 + returns[bench]
    ).cumprod()

    fig.add_trace(

        go.Scatter(
            x=bench_curve.index,
            y=bench_curve,
            name=bench
        )

    )
```

st.plotly_chart(
fig,
use_container_width=True
)

# ==========================================

# CORRELATION

# ==========================================

st.subheader(
"Correlation Matrix"
)

corr = (
returns[tickers]
.corr()
)

st.dataframe(
corr.round(2)
)

fig_corr = px.imshow(
corr,
text_auto=".2f",
color_continuous_scale="RdBu"
)

st.plotly_chart(
fig_corr,
use_container_width=True
)

# ==========================================

# DRAWDOWN

# ==========================================

st.subheader(
"Drawdown"
)

fig_dd = go.Figure()

fig_dd.add_trace(

```
go.Scatter(
    x=dd_series.index,
    y=dd_series,
    name="Drawdown"
)
```

)

st.plotly_chart(
fig_dd,
use_container_width=True
)
