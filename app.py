import streamlit as st
import webbrowser
import yfinance as yf
import pandas as pd
import time

st.set_page_config(page_title="Smart Stock Scanner", layout="centered")

st.title("📊 Smart Stock Scanner (Pro Auto Mode)")
st.write("NIFTY50 + Defence + Renewable | Breakout + RSI + Volume + Trend")

# ---------------- STOCK LIST ---------------- #

nifty50 = [
    "RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","ICICIBANK.NS",
    "LT.NS","SBIN.NS","AXISBANK.NS","KOTAKBANK.NS","ITC.NS",
    "BHARTIARTL.NS","ASIANPAINT.NS","MARUTI.NS","HCLTECH.NS",
    "SUNPHARMA.NS","TITAN.NS","ULTRACEMCO.NS","NESTLEIND.NS",
    "BAJFINANCE.NS","BAJAJFINSV.NS","WIPRO.NS","TECHM.NS",
    "POWERGRID.NS","NTPC.NS","ONGC.NS","COALINDIA.NS",
    "ADANIPORTS.NS","ADANIENT.NS","JSWSTEEL.NS","TATASTEEL.NS",
    "GRASIM.NS","HINDALCO.NS","DRREDDY.NS","CIPLA.NS",
    "DIVISLAB.NS","BRITANNIA.NS","HEROMOTOCO.NS","EICHERMOT.NS",
    "BAJAJ-AUTO.NS","SHREECEM.NS","APOLLOHOSP.NS","HDFCLIFE.NS",
    "SBILIFE.NS","INDUSINDBK.NS","UPL.NS","TATACONSUM.NS",
    "M&M.NS","TATAMOTORS.NS","BPCL.NS","IOC.NS"
]

defence = [
    "HAL.NS","BEL.NS","BEML.NS","MAZDOCK.NS","COCHINSHIP.NS",
    "GRSE.NS","BDL.NS"
]

renewable = [
    "TATAPOWER.NS","ADANIGREEN.NS","NHPC.NS","BORORENEW.NS",
    "JSWENERGY.NS","SUZLON.NS","INDIAGLYCO.NS"
]

# Merge + remove duplicates
stocks = list(set(nifty50 + defence + renewable))

# ---------------- RSI ---------------- #

def calculate_rsi(close, period=14):
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

# ---------------- SIGNAL ---------------- #

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
    recent_high = float(close.iloc[-6:-1].max())

    avg_vol = volume.iloc[-6:-1].mean()
    today_vol = volume.iloc[-1]

    # Trend
    ma50 = close.rolling(50).mean().iloc[-1]
    ma200 = close.rolling(200).mean().iloc[-1]

    uptrend = ma50 > ma200

    if last > recent_high and 40 < rsi < 70 and today_vol > avg_vol and uptrend:
        return "STRONG BUY", rsi, last
    else:
        return "HOLD", rsi, last

# ---------------- ZERODHA ---------------- #

def open_in_kite(stock):
    stock_name = stock.replace(".NS", "")
    url = f"https://kite.zerodha.com/chart/web/tvc/NSE/{stock_name}/{stock_name}"
    webbrowser.open(url)

# ---------------- UI ---------------- #

st.subheader(f"📊 Scanning {len(stocks)} Stocks")

results = []

for stock in stocks:
    signal, rsi, price = get_signal(stock)

    if signal == "STRONG BUY":
        results.append((stock, rsi, price))

# Sort best
results = sorted(results, key=lambda x: x[1])

if results:
    st.success("🔥 High Quality Trades Found")

    for i, (stock, rsi, price) in enumerate(results[:5]):

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

# Auto refresh
time.sleep(300)
st.rerun()