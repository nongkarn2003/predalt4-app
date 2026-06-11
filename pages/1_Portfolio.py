import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ==================================

# CONFIG

# ==================================

st.set_page_config(
page_title="Portfolio Dashboard",
page_icon="📈",
layout="wide"
)

st.title("📈 Portfolio Analytics Dashboard")

# ==================================

# SIDEBAR

# ==================================

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
st.sidebar.markdown(f"### Asset {i+1}")

ticker = st.sidebar.text_input(
    f"Ticker {i+1}",
    key=f"ticker_{i}"
)

weight = st.sidebar.number_input(
    f"Weight {i+1}",
    min_value=0.0,
    value=0.0,
    step=1.0,
    key=f"weight_{i}"
)

if ticker != "":
    tickers.append(
        ticker.upper()
    )
    weights.append(weight)
```

# ==================================

# BENCHMARK

# ==================================

st.sidebar.header("Benchmarks")

num_bench = st.sidebar.number_input(
"Number of Benchmarks",
min_value=1,
max_value=10,
value=3
)

benchmarks = []

for i in range(num_bench):

```
bench = st.sidebar.text_input(
    f"Benchmark {i+1}",
    key=f"bench_{i}"
)

if bench != "":
    benchmarks.append(
        bench.upper()
    )
```

# ==================================

# SETTINGS

# ==================================

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
value=0.04,
step=0.01
)

run_button = st.sidebar.button(
"🚀 Run Analysis"
)

# ==================================

# STOP

# ==================================

if not run_button:
st.info("Please input portfolio and click Run Analysis")
st.stop()

# ==================================

# VALIDATION

# ==================================

if len(tickers) == 0:

```
st.error("Please enter at least one ticker")
st.stop()
```

weights = np.array(weights)

if weights.sum() == 0:

```
st.error("Weights cannot sum to zero")
st.stop()
```

weights = weights / weights.sum()

# ==================================

# DOWNLOAD DATA

# ==================================

all_tickers = list(
set(
tickers + benchmarks
)
)

with st.spinner("Downloading data..."):

```
data = yf.download(
    all_tickers,
    start=start_date,
    end=end_date,
    auto_adjust=True,
    progress=False
)
```

# ==================================

# FIX YFINANCE

# ==================================

try:
close = data["Close"]

except:
close = data.xs(
"Close",
axis=1,
level=0
)

close = close.ffill()

close = close.dropna(
how="all"
)

returns = close.pct_change().dropna()

# ==================================

# PORTFOLIO RETURN

# ==================================

portfolio_returns = (
returns[tickers] * weights
).sum(axis=1)

# ==================================

# FUNCTIONS

# ==================================

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
vol = annual_vol(r)

if vol == 0:
    return np.nan

return (
    annual_return(r)
    - rf
) / vol
```

def max_drawdown(r):

```
wealth = (
    1+r
).cumprod()

peak = wealth.cummax()

dd = (
    wealth - peak
) / peak

return dd.min(), dd
```

def var95(r):

```
return np.percentile(
    r,
    5
)
```

# ==================================

# PERIOD RETURNS

# ==================================

def period_return(
r,
months=None,
years=None
):

```
end = r.index[-1]

if months:
    start = (
        end -
        pd.DateOffset(
            months=months
        )
    )

elif years:
    start = (
        end -
        pd.DateOffset(
            years=years
        )
    )

else:
    return np.nan

sub = r[
    r.index >= start
]

if len(sub) < 2:
    return np.nan

return (
    1+sub
).prod() - 1
```

# ==================================

# METRICS

# ==================================

mdd, dd_series = max_drawdown(
portfolio_returns
)

# ==================================

# KPI

# ==================================

c1,c2,c3,c4,c5 = st.columns(5)

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
"VaR",
f"{var95(portfolio_returns):.2%}"
)

c5.metric(
"Max Drawdown",
f"{mdd:.2%}"
)

# ==================================

# RETURNS TABLE

# ==================================

st.subheader("Portfolio Returns")

returns_df = pd.DataFrame({

```
"Period":[
    "1M",
    "6M",
    "1Y",
    "5Y",
    "10Y"
],

"Return":[

    period_return(
        portfolio_returns,
        months=1
    ),

    period_return(
        portfolio_returns,
        months=6
    ),

    period_return(
        portfolio_returns,
        years=1
    ),

    period_return(
        portfolio_returns,
        years=5
    ),

    period_return(
        portfolio_returns,
        years=10
    )

]
```

})

st.dataframe(
returns_df.style.format({
"Return":"{:.2%}"
})
)

# ==================================

# CORRELATION

# ==================================

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

# ==================================

# EQUITY CURVE

# ==================================

st.subheader(
"Portfolio Growth"
)

curve = (
1+portfolio_returns
).cumprod()

fig = go.Figure()

fig.add_trace(

```
go.Scatter(
    x=curve.index,
    y=curve,
    name="Portfolio"
)
```

)

st.plotly_chart(
fig,
use_container_width=True
)

# ==================================

# DRAWDOWN

# ==================================

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
