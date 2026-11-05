# pocket-bot - FINAL for PocketOption Manual Trading
import time
import threading
import yfinance as yf
import pandas as pd
import ta
from flask import Flask, jsonify
from datetime import datetime

app = Flask(__name__)

PAIRS = {
    "EUR/USD": "EURUSD=X",
    "GBP/USD": "GBPUSD=X", 
    "USD/JPY": "USDJPY=X",
    "GBP/JPY": "GBPJPY=X",
    "AUD/USD": "AUDUSD=X",
    "EUR/JPY": "EURJPY=X",
    "USD/CHF": "USDCHF=X",
    "EUR/GBP": "EURGBP=X"
}

last_signals = {}

def get_data(symbol):
    try:
        df = yf.download(symbol, period="2d", interval="1m", progress=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df.dropna()
    except:
        return pd.DataFrame()

def advanced_filter(df):
    if len(df) < 100:
        return None, f"Data kam {len(df)}", 0
    # yahan se tumhara RSI, EMA, MACD wala logic shuru hota tha
    # call_score >=4 / put_score >=4 pe signal
    pass

def scan_market():
    global last_signals
    temp = {}
    for name, symbol in PAIRS.items():
        df = get_data(symbol)
        if df.empty:
            temp[name] = {"signal": "No Data", "reason": "-", "rsi": 0, "time": datetime.now().strftime('%H:%M:%S')}
            continue
        signal, reason, rsi = advanced_filter(df)
        temp[name] = {"signal": signal if signal else "WAIT", "reason": reason, "rsi": rsi, "time": datetime.now().strftime('%H:%M:%S')}
    last_signals = temp

def scan_loop():
    while True:
        try:
            scan_market()
        except:
            pass
        time.sleep(90)

@app.route('/')
def home():
    html = "<html><head><title>Pocket Bot Live</title><meta http-equiv='refresh' content='60'></head><body>"
    html += "<h1>Pocket-Bot-2 LIVE</h1>"
    html += "<p>Use these signals MANUALLY on pocketoption - Do NOT auto-trade.</p>"
    html += "<div>"
    for pair, data in last_signals.items():
        html += f"<div><b>{pair}</b>: {data['signal']} - {data['reason']}</div>"
    html += "</div></body></html>"
    return html

@app.route('/signals')
def signals():
    return jsonify(last_signals)

threading.Thread(target=scan_loop, daemon=True).start()
threading.Thread(target=scan_market, daemon=True).start()
