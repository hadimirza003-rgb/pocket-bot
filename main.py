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
        return None, "Data kam hai", 0
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
        return None, f"Slow Market", int(last_rsi)
    if abs(last_ema9 - last_ema21) < 0.0001:
        return None, "Sideways", int(last_rsi)

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
        return f"STRONG CALL", f"Score {call_score}/5 RSI {last_rsi:.1f}", int(last_rsi)
    if put_score >= 4:
        return f"STRONG PUT", f"Score {put_score}/5 RSI {last_rsi:.1f}", int(last_rsi)

    return None, f"RSI {last_rsi:.1f} C:{call_score} P:{put_score}", int(last_rsi)

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
    html = "<html><head><title>Pocket Bot Live</title><meta http-equiv='refresh' content='60'>"
    html += "<style>body{font-family:sans-serif;background:#111;color:#fff;padding:20px} .card{background:#222;padding:15px;margin:10px;border-radius:10px;display:inline-block;width:200px} .call{border-left:5px solid #00ff88} .put{border-left:5px solid #ff4444} .wait{border-left:5px solid #555} h1{color:#00ff88} a{color:#0af}</style></head><body>"
    html += "<h1>Pocket-Bot-2 LIVE</h1>"
    html += "<p>Use these signals MANUALLY on pocketoption - Do NOT auto-trade.</p>"
    html += "<p>Auto refresh every 60 sec</p><div>"
    for pair, data in last_signals.items():
        cls = "call" if "CALL" in data['signal'] else "put" if "PUT" in data['signal'] else "wait"
        emoji = "🟢" if "CALL" in data['signal'] else "🔴" if "PUT" in data['signal'] else "⏳"
        html += f"<div class='card {cls}'><b>{pair}</b><br>{emoji} {data['signal']}<br><small>{data['reason']}</small></div>"
    html += "</div></body></html>"
    return html

@app.route('/signals')
def signals():
    return jsonify(last_signals)

threading.Thread(target=scan_loop, daemon=True).start()
threading.Thread(target=scan_market, daemon=True).start()
