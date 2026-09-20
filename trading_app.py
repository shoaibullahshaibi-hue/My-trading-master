import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

st.set_page_config(page_title="Trading Analysis", page_icon="📈", layout="wide")
st.title("📈 ICT Trading Analysis")

assets = {
    "Gold": "GC=F",
    "Bitcoin": "BTC-USD",
    "Ethereum": "ETH-USD",
    "Solana": "SOL-USD",
    "BNB": "BNB-USD",
    "XRP": "XRP-USD",
}

st.sidebar.title("Settings")
name = st.sidebar.selectbox("Asset:", list(assets.keys()))
period = st.sidebar.selectbox("Period:", ["1mo", "3mo", "6mo"])
interval = st.sidebar.selectbox("Timeframe:", ["1d", "1h", "15m"])

symbol = assets[name]
df = yf.download(symbol, period=period, interval=interval, progress=False)
close = df['Close'].squeeze()
high = df['High'].squeeze()
low = df['Low'].squeeze()

current = float(close.iloc[-1])
prev = float(close.iloc[-2])
change = ((current - prev) / prev) * 100

# Indicators
ma20 = close.rolling(20).mean()
ma50 = close.rolling(50).mean()
ma200 = close.rolling(200).mean()

delta = close.diff()
gain = delta.where(delta > 0, 0).rolling(14).mean()
loss = -delta.where(delta < 0, 0).rolling(14).mean()
rsi = (100 - (100 / (1 + gain/loss))).iloc[-1]

ema12 = close.ewm(span=12).mean()
ema26 = close.ewm(span=26).mean()
macd = (ema12 - ema26).iloc[-1]
signal_line = (ema12 - ema26).ewm(span=9).mean().iloc[-1]

bb_mid = close.rolling(20).mean()
bb_std = close.rolling(20).std()
bb_upper = (bb_mid + 2*bb_std).iloc[-1]
bb_lower = (bb_mid - 2*bb_std).iloc[-1]

atr = (high - low).rolling(14).mean().iloc[-1]

resistance = high.rolling(20).max().iloc[-1]
support = low.rolling(20).min().iloc[-1]

# Entry, SL, TP
if rsi < 40 and macd > signal_line and current > float(ma20.iloc[-1]):
    direction = "LONG"
    entry = current
    sl = current - (atr * 1.5)
    tp1 = current + (atr * 2)
    tp2 = current + (atr * 3.5)
    tp3 = float(resistance)
    signal_color = "🟢"
elif rsi > 60 and macd < signal_line and current < float(ma20.iloc[-1]):
    direction = "SHORT"
    entry = current
    sl = current + (atr * 1.5)
    tp1 = current - (atr * 2)
    tp2 = current - (atr * 3.5)
    tp3 = float(support)
    signal_color = "🔴"
else:
    direction = "WAIT"
    entry = current
    sl = current - (atr * 1.5)
    tp1 = current + (atr * 2)
    tp2 = current + (atr * 3)
    tp3 = float(resistance)
    signal_color = "⏳"

rr = abs(tp1 - entry) / abs(entry - sl) if abs(entry - sl) > 0 else 0

# Metrics
st.subheader(f"{signal_color} {name} — {direction}")
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Price", f"${current:,.2f}", f"{change:+.2f}%")
col2.metric("RSI", f"{rsi:.1f}")
col3.metric("Support", f"${support:,.2f}")
col4.metric("Resistance", f"${resistance:,.2f}")
col5.metric("ATR", f"${atr:,.2f}")

st.divider()

# Trade Setup
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Entry", f"${entry:,.2f}")
col2.metric("🔴 Stop Loss", f"${sl:,.2f}")
col3.metric("🎯 TP1", f"${tp1:,.2f}")
col4.metric("🎯 TP2", f"${tp2:,.2f}")
col5.metric("🎯 TP3", f"${tp3:,.2f}")

st.info(f"Risk:Reward = 1:{rr:.1f} | BB Upper: ${bb_upper:,.2f} | BB Lower: ${bb_lower:,.2f}")

# Chart
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), gridspec_kw={'height_ratios': [3, 1]})
fig.patch.set_facecolor('#0e1117')
ax1.set_facecolor('#0e1117')
ax2.set_facecolor('#0e1117')

ax1.plot(df.index, close, color='white', linewidth=1.5, label='Price')
ax1.plot(df.index, ma20, color='orange', linewidth=1, linestyle='--', label='MA20')
ax1.plot(df.index, ma50, color='red', linewidth=1, linestyle='--', label='MA50')
ax1.plot(df.index, bb_mid, color='blue', linewidth=0.8, linestyle='--', label='BB Mid')
ax1.fill_between(df.index, bb_mid + 2*bb_std, bb_mid - 2*bb_std, alpha=0.1, color='blue', label='BB Bands')

ax1.axhline(y=resistance, color='#00ff88', linestyle=':', linewidth=1, label='Resistance')
ax1.axhline(y=support, color='#ff4444', linestyle=':', linewidth=1, label='Support')
ax1.axhline(y=entry, color='white', linestyle='-', linewidth=1.5, label='Entry')
ax1.axhline(y=sl, color='red', linestyle='--', linewidth=1.5, label='SL')
ax1.axhline(y=tp1, color='#00ff88', linestyle='--', linewidth=1, label='TP1')
ax1.axhline(y=tp2, color='#00cc66', linestyle='--', linewidth=1, label='TP2')
ax1.axhline(y=tp3, color='#009944', linestyle='--', linewidth=1, label='TP3')

ax1.set_title(f'{name} Chart', color='white', fontsize=14)
ax1.tick_params(colors='white')
ax1.spines['bottom'].set_color('#333')
ax1.spines['left'].set_color('#333')
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.legend(facecolor='#1a1a2e', labelcolor='white', fontsize=7, loc='upper left')
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))

delta2 = close.diff()
gain2 = delta2.where(delta2 > 0, 0).rolling(14).mean()
loss2 = -delta2.where(delta2 < 0, 0).rolling(14).mean()
rsi_line = 100 - (100 / (1 + gain2/loss2))
ax2.plot(df.index, rsi_line, color='purple', linewidth=1.5)
ax2.axhline(y=70, color='red', linestyle='--', linewidth=0.8)
ax2.axhline(y=30, color='green', linestyle='--', linewidth=0.8)
ax2.fill_between(df.index, rsi_line, 70, where=(rsi_line >= 70), alpha=0.3, color='red')
ax2.fill_between(df.index, rsi_line, 30, where=(rsi_line <= 30), alpha=0.3, color='green')
ax2.set_title('RSI', color='white', fontsize=10)
ax2.tick_params(colors='white')
ax2.spines['bottom'].set_color('#333')
ax2.spines['left'].set_color('#333')
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.set_ylim(0, 100)
ax2.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))

plt.xticks(rotation=45, color='white')
plt.tight_layout()
st.pyplot(fig)
plt.close()

st.caption(f"Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
