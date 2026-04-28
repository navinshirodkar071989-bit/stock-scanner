import streamlit as st
import webbrowser
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Smart Stock Scanner", layout="centered")

st.title("📊 Smart Stock Scanner (Pro Mode)")
st.write("Breakout + RSI + Volume + Trend Filter")

# Expanded stock list (NIFTY style)
stocks = [
    "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS",
    "LT.NS", "SBIN.NS", "AXISBANK.NS", "KOTAKBANK.NS", "ITC.NS",
    "BHARTIARTL.NS", "ASIANPAINT.NS", "MARUTI.NS", "HCLTECH.NS",
    "SUNPHARMA.NS", "TITAN.NS", "ULTRACEMCO.NS", "NESTLEIND.NS"
]

# RSI
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

    # RSI
    rsi_series = calculate_rsi(close).dropna()
    if len(rsi_series) == 0:
        return "HOLD", 0, 0

    rsi = float(rsi_series.iloc[-1])

    # Price
    last = float(close.iloc[-1])
    prev = float(close.iloc[-2])

    # Breakout
    recent_high = float(close.iloc[-6:-1].max())

    # Volume
    avg_vol = volume.iloc[-6:-1].mean()
    today_vol = volume.iloc[-1]

    # 🔥 Trend filter (50 DMA vs 200 DMA)
    ma50 = close.rolling(50).mean().iloc[-1]
    ma200 = close.rolling(200).mean().iloc[-1]

    uptrend = ma50 > ma200

    # Final condition
    if (last > recent_high and 
        40 < rsi < 70 and 
        today_vol > avg_vol and 
        uptrend):

        return "STRONG BUY", rsi, last
    else:
        return "HOLD", rsi, last

# Open Zerodha
def open_in_kite(stock):
    stock_name = stock.replace(".NS", "")
    url = f"https://kite.zerodha.com/chart/web/tvc/NSE/{stock_name}/{stock_name}"
    webbrowser.open(url)

# UI
if st.button("🔍 Scan Stocks"):

    st.subheader("📊 Scan Results")

    results = []

    for stock in stocks:
        signal, rsi, price = get_signal(stock)

        if signal == "STRONG BUY":
            results.append((stock, rsi, price))

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
        st.warning("No strong trend breakout stocks today")
