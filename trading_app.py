import streamlit as st
import yfinance as yf
import matplotlib.pyplot as plt

st.title("Trading Analysis")

assets = {"Gold": "GC=F", "Bitcoin": "BTC-USD", "Ethereum": "ETH-USD"}
name = st.selectbox("Asset:", list(assets.keys()))

df = yf.download(assets[name], period="3mo", interval="1d", progress=False)
close = df['Close'].squeeze()
current = float(close.iloc[-1])
change = ((current - float(close.iloc[-2])) / float(close.iloc[-2])) * 100

st.metric("Price", f"${current:,.2f}", f"{change:+.2f}%")

fig, ax = plt.subplots(figsize=(10,4))
ax.plot(df.index, close)
ax.set_title(name)
st.pyplot(fig)
plt.close()
