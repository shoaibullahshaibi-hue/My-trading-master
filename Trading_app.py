import streamlit as st
import yfinance as yf
import matplotlib.pyplot as plt

st.title("ICT Mobile")

pairs = {"BTC": "BTC-USD", "ETH": "ETH-USD", "SOL": "SOL-USD", "Gold": "GC=F"}
symbol = st.sidebar.selectbox("Pair", list(pairs.keys()))

try:
    df = yf.download(pairs[symbol], period="1mo", interval="1d", progress=False)
    
    if df.empty:
        st.error("Data nahi mila — dobara try karo!")
    else:
        current = float(df['Close'].iloc[-1])
        high = float(df['High'].rolling(20).max().iloc[-1])
        low = float(df['Low'].rolling(20).min().iloc[-1])
        eq = (high + low) / 2

        st.metric("Price", f"${current:,.2f}")
        st.metric("State", "DISCOUNT 🟢" if current < eq else "PREMIUM 🔴")
        st.metric("Equilibrium", f"${eq:,.2f}")
        st.metric("Swing High", f"${high:,.2f}")
        st.metric("Swing Low", f"${low:,.2f}")

        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(df.index, df['Close'], color='white', linewidth=1.5)
        ax.axhline(eq, color='yellow', linestyle='--', label='EQ')
        ax.axhline(high, color='#00ff88', linestyle=':', label='High')
        ax.axhline(low, color='#ff4444', linestyle=':', label='Low')
        ax.set_facecolor('#0e1117')
        fig.patch.set_facecolor('#0e1117')
        ax.tick_params(colors='white')
        ax.legend(facecolor='#1a1a2e', labelcolor='white')
        st.pyplot(fig)
        plt.close()

except Exception as e:
    st.error(f"Error: {e}")
