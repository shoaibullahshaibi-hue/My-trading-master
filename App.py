import streamlit as st
import yfinance as yf
import matplotlib.pyplot as plt

st.title("ICT Mobile")

pairs = {"BTC": "BTC-USD", "ETH": "ETH-USD", "SOL": "SOL-USD", "Gold": "GC=F"}
symbol = st.sidebar.selectbox("Pair", list(pairs.keys()))

df = yf.download(pairs[symbol], period="1mo", interval="1d", progress=False)
current = float(df['Close'].iloc[-1])
high = float(df['High'].rolling(20).max().iloc[-1])
low = float(df['Low'].rolling(20).min().iloc[-1])
eq = (high + low) / 2

st.metric("Price", f"${current:,.2f}")
st.metric("State", "DISCOUNT" if current < eq else "PREMIUM")

fig, ax = plt.subplots()
ax.plot(df.index, df['Close'], color='white')
ax.axhline(eq, color='yellow', linestyle='--')
ax.set_facecolor('#0e1117')
fig.patch.set_facecolor('#0e1117')
ax.tick_params(colors='white')
st.pyplot(fig)
plt.close()
