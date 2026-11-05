import os
import time
import threading
import yfinance as yf
import pandas as pd
import ta
from flask import Flask, jsonify
from datetime import datetime

TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

try:
    import telebot
    bot = telebot.TeleBot(TOKEN) if TOKEN else None
except:
    bot = None

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
last_sent = {}

def get_data(s, i="1m", p="2d"):
    try:
        df = yf.download(s, period=p, interval=i, progress=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df.dropna()
    except:
        return pd.DataFrame()

def filt(df1, df5):
    if len(df1) < 100 or len(df5) < 50:
        return None, "Wait", 0
    
    c = df1['Close']
    h = df1['High']
    l = df1['Low']
    
    r = ta.momentum.RSIIndicator(c, 14).rsi()
    e9 = ta.trend.EMAIndicator(c, 9).ema_indicator()
    e21 = ta.trend.EMAIndicator(c, 21).ema_indicator()
    e50 = ta.trend.EMAIndicator(c, 50).ema_indicator()
    m = ta.trend.MACD(c)
    md = m.macd_diff()
    ml = m.macd()
    bb = ta.volatility.BollingerBands(c, 20, 2)
    bbh = bb.bollinger_hband()
    bbl = bb.bollinger_lband()
    atr = ta.volatility.AverageTrueRange(h, l, c, 14).average_true_range()
    st = ta.momentum.StochasticOscillator(h, l, c).stoch()
    
    lc = c.iloc[-1]
    lr = r.iloc[-1]
    le9 = e9.iloc[-1]
    le21 = e21.iloc[-1]
    le50 = e50.iloc[-1]
    lmd = md.iloc[-1]
    lml = ml.iloc[-1]
    lbh = bbh.iloc[-1]
    lbl = bbl.iloc[-1]
    la = atr.iloc[-1]
    ls = st.iloc[-1]
    pc = c.iloc[-2]
    pe9 = e9.iloc[-2]
    
    c5 = df5['Close']
    e9_5 = ta.trend.EMAIndicator(c5, 9).ema_indicator()
    e21_5 = ta.trend.EMAIndicator(c5, 21).ema_indicator()
    up = e9_5.iloc[-1] > e21_5.iloc[-1]
    down = e9_5.iloc[-1] < e21_5.iloc[-1]
    
    if la < 0.00035:
        return None, f"Slow {la:.5f}", int(lr)
    if abs(le9 - le21) < 0.00012:
        return None, "Sideways", int(lr)
    if abs(lc - le50) > la * 5:
        return None, "Far EMA50", int(lr)
        
    cs = 0
    ps = 0
    if lr < 28: cs += 1
    if lr > 72: ps += 1
    if le9 > le21 and lc > le21: cs += 1
    if le9 < le21 and lc < le21: ps += 1
    if lmd > 0 and lml > 0: cs += 1
    if lmd < 0 and lml < 0: ps += 1
    if lc <= lbl * 1.001 and ls < 20: cs += 1
    if lc >= lbh * 0.999 and ls > 80: ps += 1
    if pc < pe9 and lc > le9 and lc > le21: cs += 1
    if pc > pe9 and lc < le9 and lc < le21: ps += 1
    if up: cs += 1
    if down: ps += 1
    
    if cs >= 5:
        return "STRONG CALL", f"{cs}/6 UP RSI{lr:.0f}", int(lr)
    if ps >= 5:
        return "STRONG PUT", f"{ps}/6 DOWN RSI{lr:.0f}", int(lr)
        
    return None, f"WAIT R{lr:.0f} C:{cs} P:{ps}", int(lr)

def send(msg):
    if not bot or not CHAT_ID:
        return
    try:
        bot.send_message(CHAT_ID, msg, parse_mode="Markdown")
    except:
        pass

def scan():
    global last_signals
    tmp = {}
    for n, s in PAIRS.items():
        d1 = get_data(s, "1m", "2d")
        d5 = get_data(s, "5m", "5d")
        if d1.empty or d5.empty:
            tmp[n] = {"signal": "No Data", "reason": "-", "rsi": 0, "time": datetime.now().strftime('%H:%M:%S')}
            continue
        sig, rsi_val, rsi = filt(d1, d5)
        tmp[n] = {"signal": sig if sig else "WAIT", "reason": rsi_val, "rsi": rsi, "time": datetime.now().strftime('%H:%M:%S')}
        
        if sig and last_sent.get(n) != sig:
            send(f"🚨 *SUPER STRICT Signal* 🚨\n📊 {n}\n⚡ {sig}\n📝 {rsi_val}\n🕒 {datetime.now().strftime('%H:%M:%S')}\nTrade: m.pocketoption.com/en/cabinet/")
            last_sent[n] = sig
        if not sig:
            last_sent[n] = None
            
    last_signals = tmp

def loop():
    while True:
        try:
            scan()
        except:
            pass
        time.sleep(120)

@app.route('/')
def home():
    h = "<h1>Super Strict Bot Live</h1><p>Telegram: " + ("ON" if bot and CHAT_ID else "OFF") + " | <a href='/signals'>JSON</a></p>"
    for p, d in last_signals.items():
        h += f"<div><b>{p}</b>: {d['signal']} - {d['reason']}</div>"
    return h

@app.route('/signals')
def signals():
    return jsonify(last_signals)

if __name__ == '__main__':
    threading.Thread(target=loop, daemon=True).start()
    threading.Thread(target=scan, daemon=True).start()
    
    # Render ke liye port binding zaroori hai
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
