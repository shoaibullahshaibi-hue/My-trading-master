
import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

st.set_page_config(page_title="Trading Analysis", page_icon="📈", layout="wide")
st.title("📈 Live Trading Analysis")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

assets = {
    "🥇 Gold": "GC=F",
    "₿ Bitcoin": "BTC-USD",
    "Ξ Ethereum": "ETH-USD",
    "◎ Solana": "SOL-USD",
    "BNB": "BNB-USD",
    "✕ XRP": "XRP-USD",
}

selected = st.sidebar.multiselect(
    "Assets Select Karo:",
    list(assets.keys()),
    default=list(assets.keys())
)

interval = st.sidebar.selectbox("Timeframe:", ["1d", "1h", "15m", "5m"])
period = st.sidebar.selectbox("Period:", ["1mo", "3mo", "6mo", "1y"])
auto_refresh = st.sidebar.checkbox("Auto Refresh (30 sec)", value=True)

if auto_refresh:
    import time
    st.sidebar.info("Auto refresh ON")

def get_signal(close, rsi, macd_val, sig_val, ma20):
    current = close.iloc[-1]
    if rsi < 35 and macd_val > sig_val and current > ma20:
        return "✅ BUY", "green"
    elif rsi > 65 and macd_val < sig_val and current < ma20:
        return "❌ SELL", "red"
    else:
        return "⏳ WAIT", "orange"

for name in selected:
    symbol = assets[name]
    
    with st.expander(f"{name}", expanded=True):
        try:
            df = yf.download(symbol, period=period, interval=interval, progress=False)
            close = df['Close'].squeeze()
            high = df['High'].squeeze()
            low = df['Low'].squeeze()
            volume = df['Volume'].squeeze()
            
            current = close.iloc[-1]
            prev = close.iloc[-2]
            change = ((current - prev) / prev) * 100
            
            ma20 = close.rolling(20).mean()
            ma50 = close.rolling(50).mean()
            
            delta = close.diff()
            gain = delta.where(delta > 0, 0).rolling(14).mean()
            loss = -delta.where(delta < 0, 0).rolling(14).mean()
            rsi = (100 - (100 / (1 + gain/loss))).iloc[-1]
            
            ema12 = close.ewm(span=12).mean()
            ema26 = close.ewm(span=26).mean()
            macd = (ema12 - ema26).iloc[-1]
            signal = (ema12 - ema26).ewm(span=9).mean().iloc[-1]
            
            resistance = high.rolling(20).max().iloc[-1]
            support = low.rolling(20).min().iloc[-1]
            
            sig_text, sig_color = get_signal(close, rsi, macd, signal, ma20.iloc[-1])
            
            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("Price", f"${current:.2f}", f"{change:+.2f}%")
            col2.metric("RSI", f"{rsi:.1f}")
            col3.metric("Support", f"${support:.2f}")
            col4.metric("Resistance", f"${resistance:.2f}")
            col5.metric("Signal", sig_text)
            
            fig, ax = plt.subplots(figsize=(12, 4))
            ax.plot(df.index, close, linewidth=2, color='blue', label='Price')
            ax.plot(df.index, ma20, linestyle='--', color='orange', label='MA20')
            ax.plot(df.index, ma50, linestyle='--', color='red', label='MA50')
            ax.fill_between(df.index, high.rolling(20).max(), low.rolling(20).min(), alpha=0.1, color='green')
            ax.set_title(f'{name} Chart')
            ax.legend()
            ax.grid(True, alpha=0.3)
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()
            
        except Exception as e:
            st.error(f"Data load error: {e}")

if auto_refresh:
    import time
    time.sleep(30)
    st.rerun()
