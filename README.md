## 📈 Financial Strategy Dashboard

A simple Streamlit app that lets you backtest two common trading strategies using real historical stock data.

### 💡 Features
- Choose any stock ticker
- Pick date range and strategy
- View cumulative returns vs. market
- See key metrics like Sharpe ratio and volatility

### ⚙️ Strategies Included
- **Momentum**: Buy when price > 50-day moving average  
- **Mean Reversion**: Buy when RSI < 30

### ▶️ How to Run

```bash
pip install -r requirements.txt
streamlit run app.py
