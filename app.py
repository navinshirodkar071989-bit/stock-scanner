import streamlit as st
import webbrowser
import yfinance as yf
import pandas as pd
import time

st.set_page_config(page_title="Smart Stock Scanner", layout="centered")

st.title("📊 Smart Stock Scanner (Auto Mode)")
st.write("Breakout + RSI + Volume + Trend Filter (Auto Scan Every 5 min)")

# Stocks to scan
stocks = [
    "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS",
    "LT.NS", "SBIN.NS", "AXISBANK.NS", "KOTAKBANK.NS", "ITC.NS",
    "BHARTIARTL.NS", "ASIANPAINT.NS", "MARUTI.NS", "HCLTECH.NS",
    "SUNPHARMA.NS", "TITAN.NS", "ULTRACEMCO.NS", "NESTLEIND.NS"
]

# RSI calculation
def calculate_rsi(close, period=14):
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

# Signal logic
def get_signal(stock):
    data = yf.download(stock, period="3mo", interval="1d", progress=False)

    if data.empty or len(data) < 50:
        return "HOLD", 0, 0

    close = data["Close"]
    volume = data["Volume"]

    if isinstance(close, pd.DataFrame):
        close = close.iloc[:, 0]
    if isinstance(volume, pd.DataFrame):
        volume = volume.iloc[:, 0]

    close = close.dropna()
    volume = volume.dropna()

    rsi_series = calculate_rsi(close).dropna()
    if len(rsi_series) == 0:
        return "HOLD", 0, 0

    rsi = float(rsi_series.iloc[-1])

    last = float(close.iloc[-1])
    prev = float(close.iloc[-2])
    recent_high = float(close.iloc[-6:-1].max())

    avg_vol = volume.iloc[-6:-1].mean()
    today_vol = volume.iloc[-1]

    # Trend filter
    ma50 = close.rolling(50).mean().iloc[-1]
    ma200 = close.rolling(200).mean().iloc[-1]

    uptrend = ma50 > ma200

    if last > recent_high and 40 < rsi < 70 and today_vol > avg_vol and uptrend:
        return "STRONG BUY", rsi, last
    else:
        return "HOLD", rsi, last

# Open in Zerodha
def open_in_kite(stock):
    stock_name = stock.replace(".NS", "")
    url = f"https://kite.zerodha.com/chart/web/tvc/NSE/{stock_name}/{stock_name}"
    webbrowser.open(url)

# UI
st.subheader("📊 Live Auto Scan")

results = []

for stock in stocks:
    signal, rsi, price = get_signal(stock)

    if signal == "STRONG BUY":
        results.append((stock, rsi, price))

# Sort best stocks
results = sorted(results, key=lambda x: x[1])

if results:
    st.success("🔥 High Quality Trades Found")

    for i, (stock, rsi, price) in enumerate(results[:3]):

        target = price * 1.03
        stoploss = price * 0.985

        st.write(f"### {i+1}. {stock}")
        st.write(f"Entry: {round(price,2)}")
        st.write(f"Target: {round(target,2)}")
        st.write(f"Stop-loss: {round(stoploss,2)}")
        st.write(f"RSI: {round(rsi,2)}")

        if st.button(f"Open {stock} in Zerodha"):
            open_in_kite(stock)

        st.write("---")

else:
    st.warning("No strong trend breakout stocks right now")

# 🔁 Auto refresh every 5 minutes
time.sleep(300)
st.rerun()
