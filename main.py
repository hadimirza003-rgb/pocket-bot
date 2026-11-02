# main.py - Render ke liye FINAL - Web Server wala Bot
# Ye Render pe 100% chalega, Tkinter nahi hai

from flask import Flask, render_template_string, jsonify
import requests
import threading
import time
import random
from datetime import datetime
from collections import deque

app = Flask(__name__)

# Global data
price_history = deque(maxlen=100)
time_history = deque(maxlen=100)
current_signal = {"signal":"WAIT","conf":0,"price":58.5,"rsi":50,"reasons":[]}

# Seed initial
for _ in range(50):
    price_history.append(58.5 * (1 + (random.random()-0.5)*0.002))
    time_history.append(datetime.now())

def get_real_price():
    try:
        r = requests.get("https://open.er-api.com/v6/latest/USD", timeout=5)
        data = r.json()
        return data['rates']['PHP']
    except:
        return None

def calc_rsi(prices, period=14):
    if len(prices) < period+1:
        return 50
    gains, losses = 0, 0
    for i in range(1, period+1):
        diff = prices[-i] - prices[-i-1]
        if diff > 0:
            gains += diff
        else:
            losses -= diff
    if losses == 0:
        return 80
    rs = gains / losses if losses!=0 else 10
    return 100 - (100 / (1 + rs))

def update_signal():
    global current_signal
    while True:
        price = get_real_price()
        if price:
            price_history.append(price)
        else:
            price_history.append(price_history[-1] * (1 + (random.random()-0.5)*0.0003))
        
        prices = list(price_history)
        if len(prices) >= 21:
            rsi = calc_rsi(prices)
            ema9 = sum(prices[-9:])/9
            ema21 = sum(prices[-21:])/21
            sma20 = sum(prices[-20:])/20
            price_now = prices[-1]
            
            bull=bear=0
            reasons=[]
            if rsi < 45:
                bull+=1; reasons.append(f"RSI {rsi:.1f} Oversold -> CALL")
            elif rsi > 55:
                bear+=1; reasons.append(f"RSI {rsi:.1f} Overbought -> PUT")
            else:
                reasons.append(f"RSI {rsi:.1f} Neutral")
            
            if ema9 > ema21:
                bull+=1; reasons.append(f"EMA9 {ema9:.4f} > EMA21 {ema21:.4f}")
            else:
                bear+=1; reasons.append(f"EMA9 {ema9:.4f} < EMA21 {ema21:.4f}")
            
            if price_now > sma20:
                bull+=1; reasons.append(f"Price > SMA20 Uptrend")
            else:
                bear+=1; reasons.append(f"Price < SMA20 Downtrend")
            
            if bull>=2:
                signal="CALL"; conf=min(95,72+bull*7)
            elif bear>=2:
                signal="PUT"; conf=min(95,72+bear*7)
            else:
                signal="WAIT"; conf=55
            
            current_signal = {
                "signal": signal, "conf": conf, "price": price_now,
                "rsi": rsi, "ema9": ema9, "ema21": ema21, "sma20": sma20,
                "reasons": reasons, "time": datetime.now().strftime("%H:%M:%S")
            }
        time.sleep(4)

threading.Thread(target=update_signal, daemon=True).start()

HTML_PAGE = """
<!DOCTYPE html><html><head><title>QUOTEX FINAL BOT</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body{background:#0a0a0a;color:white;font-family:Arial;margin:0;padding:10px}
.card{background:#1e1e1e;border-radius:15px;padding:20px;margin:10px;text-align:center;border:2px solid #333}
.CALL{background:#002a1a;border-color:#00ff88}
.PUT{background:#2a0000;border-color:#ff4444}
.price{font-size:28px;font-weight:bold}
.signal{font-size:50px;font-weight:bold;margin:15px}
.log{background:#111;padding:10px;border-radius:10px;margin-top:15px;height:200px;overflow-y:auto;font-family:monospace;font-size:12px;color:#00ff88}
</style></head><body>
<h2 style="color:#00ff88">QUOTEX FINAL BOT - ORIGINAL - RENDER LIVE</h2>
<div id="card" class="card">
<div id="price" class="price">Loading...</div>
<div id="signal" class="signal">WAIT 🟡</div>
<div id="conf" class="conf">Confidence: 0%</div>
<div id="entry" style="font-size:20px;font-weight:bold;margin-top:10px">ENTRY: WAIT</div>
<div id="reasons" style="font-size:13px;color:#888;margin-top:10px;text-align:left"></div>
</div><div class="log" id="log"></div>
<script>
async function fetchSignal(){
  let r = await fetch('/api/signal');
  let d = await r.json();
  document.getElementById('price').innerText = 'USD/PHP: ' + d.price.toFixed(4);
  document.getElementById('signal').innerText = d.signal + (d.signal=='CALL'?' 🟢':d.signal=='PUT'?' 🔴':' 🟡
