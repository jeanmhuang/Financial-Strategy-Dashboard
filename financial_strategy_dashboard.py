import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# Page config
st.set_page_config(page_title="Financial Strategy Dashboard", layout="wide")

# Title
st.title("📈 Financial Strategy Dashboard")
st.markdown("Backtest simple trading strategies on real stock data.")

# Sidebar inputs
st.sidebar.header("Strategy Settings")
ticker = st.sidebar.text_input("Stock Ticker", value="AAPL")
start_date = st.sidebar.date_input("Start Date", value=pd.to_datetime("2020-01-01"))
end_date = st.sidebar.date_input("End Date", value=pd.to_datetime("today"))
strategy = st.sidebar.selectbox("Select Strategy", ["Momentum (50D MA)", "Mean Reversion (RSI)"])

# Download data
data = yf.download(ticker, start=start_date, end=end_date)
if data.empty:
    st.error("No data found. Please check the ticker symbol and date range.")
    st.stop()

data['Return'] = data['Adj Close'].pct_change()

# Strategy logic
def apply_momentum_strategy(df):
    df = df.copy()
    df['MA50'] = df['Adj Close'].rolling(window=50).mean()
    df['Signal'] = 0
    df.loc[df['Adj Close'] > df['MA50'], 'Signal'] = 1
    df['Strategy Return'] = df['Signal'].shift(1) * df['Return']
    return df

def apply_rsi_strategy(df, window=14):
    df = df.copy()
    delta = df['Adj Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    df['Signal'] = 0
    df.loc[df['RSI'] < 30, 'Signal'] = 1
    df['Strategy Return'] = df['Signal'].shift(1) * df['Return']
    return df

if strategy == "Momentum (50D MA)":
    strat_df = apply_momentum_strategy(data)
else:
    strat_df = apply_rsi_strategy(data)

# Cumulative returns
strat_df['Cumulative Market Return'] = (1 + strat_df['Return']).cumprod()
strat_df['Cumulative Strategy Return'] = (1 + strat_df['Strategy Return']).cumprod()

# Plot
fig = go.Figure()
fig.add_trace(go.Scatter(x=strat_df.index, y=strat_df['Cumulative Market Return'],
                         name='Market Return', line=dict(color='blue')))
fig.add_trace(go.Scatter(x=strat_df.index, y=strat_df['Cumulative Strategy Return'],
                         name='Strategy Return', line=dict(color='green')))
fig.update_layout(title=f"{ticker} Strategy Performance",
                  xaxis_title="Date", yaxis_title="Cumulative Return",
                  legend=dict(x=0, y=1), height=600)

st.plotly_chart(fig, use_container_width=True)

# Metrics
st.subheader("Performance Metrics")
sharpe_ratio = np.mean(strat_df['Strategy Return']) / np.std(strat_df['Strategy Return']) * np.sqrt(252)
total_return = strat_df['Cumulative Strategy Return'].iloc[-1] - 1
volatility = np.std(strat_df['Strategy Return']) * np.sqrt(252)

col1, col2, col3 = st.columns(3)
col1.metric("Total Return", f"{total_return:.2%}")
col2.metric("Annualized Volatility", f"{volatility:.2%}")
col3.metric("Sharpe Ratio", f"{sharpe_ratio:.2f}")
