
# pocket-bot - FINAL FIXED VERSION for Render + Python 3.14 + PTB 22.3
import os
import time
import threading
import asyncio
import yfinance as yf
import pandas as pd
import ta
from flask import Flask
from datetime import datetime

# Fix for Render event loop error
try:
    import nest_asyncio
    nest_asyncio.apply()
except:
    pass

app = Flask(__name__)

PAIRS = ["EURUSD=X", "GBPUSD=X", "USDJPY=X", "GBPJPY=X", "AUDUSD=X", "EURJPY=X"]
INTERVAL = "1m"

def get_data(symbol):
    try:
        df = yf.download(symbol, period="2d", interval=INTERVAL, progress=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df.dropna()
    except Exception as e:
        print(f"Data error {symbol}: {e}")
        return pd.DataFrame()

def advanced_filter(df):
    if len(df) < 100:
        return None, "Data kam hai"
    close = df['Close']
    high = df['High']
    low = df['Low']
    
    rsi = ta.momentum.RSIIndicator(close, 14).rsi()
    ema9 = ta.trend.EMAIndicator(close, 9).ema_indicator()
    ema21 = ta.trend.EMAIndicator(close, 21).ema_indicator()
    macd_diff = ta.trend.MACD(close).macd_diff()
    bb = ta.volatility.BollingerBands(close, 20, 2)
    bb_h = bb.bollinger_hband()
    bb_l = bb.bollinger_lband()
    atr = ta.volatility.AverageTrueRange(high, low, close, 14).average_true_range()

    last_close = close.iloc[-1]
    last_rsi = rsi.iloc[-1]
    last_ema9 = ema9.iloc[-1]
    last_ema21 = ema21.iloc[-1]
    last_macd = macd_diff.iloc[-1]
    last_bb_h = bb_h.iloc[-1]
    last_bb_l = bb_l.iloc[-1]
    last_atr = atr.iloc[-1]

    if last_atr < 0.0003:
        return None, f"Slow Market ATR {last_atr:.5f}"
    if abs(last_ema9 - last_ema21) < 0.0001:
        return None, "Sideways"

    call_score = 0
    if last_rsi < 32: call_score += 1
    if last_ema9 > last_ema21: call_score += 1
    if last_macd > 0: call_score += 1
    if last_close <= last_bb_l * 1.0005: call_score += 1
    if close.iloc[-2] < ema9.iloc[-2] and last_close > last_ema9: call_score += 1

    put_score = 0
    if last_rsi > 68: put_score += 1
    if last_ema9 < last_ema21: put_score += 1
    if last_macd < 0: put_score += 1
    if last_close >= last_bb_h * 0.9995: put_score += 1
    if close.iloc[-2] > ema9.iloc[-2] and last_close < last_ema9: put_score += 1

    if call_score >= 4:
        return f"STRONG CALL 🟢 Score {call_score}/5", f"RSI {last_rsi:.1f}"
    if put_score >= 4:
        return f"STRONG PUT 🔴 Score {put_score}/5", f"RSI {last_rsi:.1f}"

    return None, f"No Signal RSI {last_rsi:.1f} C:{call_score} P:{put_score}"

def scan_market():
    print(f"\n===== SCAN {datetime.now().strftime('%H:%M:%S')} =====", flush=True)
    for pair in PAIRS:
        df = get_data(pair)
        if df.empty:
            continue
        signal, reason = advanced_filter(df)
        name = pair.replace("=X","")
        if signal:
            print(f"✅ {name}: {signal} | {reason}", flush=True)
        else:
            print(f" - {name}: {reason}", flush=True)

def scan_loop():
    while True:
        try:
            scan_market()
        except Exception as e:
            print(f"Scan error: {e}", flush=True)
        time.sleep(120)

# Flask route for Render health check
@app.route('/')
def home():
    return "Bot Live - Strong Signal Scanner Running - 2 min scan"

# Start scanner in background thread
threading.Thread(target=scan_loop, daemon=True).start()

if __name__ == "__main__":
    # For local run
    app.run(host='0.0.0.0', port=10000)
