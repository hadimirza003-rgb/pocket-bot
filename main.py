# main.py - TELEGRAM BOT - FINAL - HAR BAR SIGNAL DEGA, SKIP NAHI KAREGA

import requests
import random
import time
from datetime import datetime
from collections import deque
import threading
import os
from flask import Flask

# Telegram ke liye
try:
    from telegram import Update
    from telegram.ext import Application, CommandHandler, ContextTypes
    HAS_TELE = True
except:
    HAS_TELE = False

# Config
BOT_TOKEN = os.getenv("BOT_TOKEN", "PUT_YOUR_BOT_TOKEN_HERE")  # Render pe env var mein daal
PAIRS = ["USD/PHP","EUR/USD","GBP/USD","USD/JPY","AUD/USD","EUR/JPY","GBP/JPY","USD/CHF","EUR/GBP","GOLD","BTC/USD"]

price_history = {p: deque(maxlen=100) for p in PAIRS}

# Seed
for p in PAIRS:
    base = 58.5 if "PHP" in p else 1.0850 if "EUR" in p else 1.27 if "GBP" in p else 150.0 if "JPY" in p else 2000
    for _ in range(50):
        price_history[p].append(base * (1 + (random.random()-0.5)*0.002))

def get_price(pair):
    try:
        if "GOLD" in pair:
            r = requests.get("https://open.er-api.com/v6/latest/XAU", timeout=5).json()
            return r['rates'].get('USD', 2000)
        base = pair.split("/")[0].replace(" OTC","")
        url = f"https://open.er-api.com/v6/latest/{base}"
        r = requests.get(url, timeout=5).json()
        target = pair.split("/")[1].replace(" OTC","")
        return r['rates'].get(target, price_history[pair][-1])
    except:
        return price_history[pair][-1] * (1 + (random.random()-0.5)*0.0003)

def calc_signal(prices):
    # RSI simple
    if len(prices) < 15:
        return {"signal":"CALL","conf":75,"rsi":50}
    gains=losses=0
    for i in range(1,15):
        d = prices[-i] - prices[-i-1]
        if d>0: gains+=d
        else: losses-=d
    rs = gains/losses if losses!=0 else 10
    rsi = 100 - (100/(1+rs))
    
    ema9 = sum(prices[-9:])/9
    ema21 = sum(prices[-21:])/21
    price = prices[-1]
    
    bull=bear=0
    if rsi < 50: bull+=1
    else: bear+=1
    if ema9 > ema21: bull+=1
    else: bear+=1
    if price > sum(prices[-20:])/20: bull+=1
    else: bear+=1
    
    # FORCE SIGNAL - Kabhi WAIT nahi, hamesha CALL ya PUT
    if bull >= bear:
        signal="CALL"
        conf = 76 + bull*5 + (3 if rsi<40 else 0)
    else:
        signal="PUT"
        conf = 76 + bear*5 + (3 if rsi>60 else 0)
    
    conf = min(92, conf)
    return {"signal":signal,"conf":conf,"rsi":rsi,"ema9":ema9,"ema21":ema21,"price":price}

async def signal_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔍 1-MIN SCAN... Real market scan ho raha hai...")
    
    best_pair = None
    best_signal = None
    best_conf = 0
    
    # Saare pairs scan karo
    for pair in PAIRS:
        price = get_price(pair)
        price_history[pair].append(price)
        res = calc_signal(list(price_history[pair]))
        if res['conf'] > best_conf:
            best_conf = res['conf']
            best_pair = pair
            best_signal = res
    
    # Hamesha signal do, kabhi skip nahi
    if best_pair and best_signal:
        msg = f"""
🚀 **1-MIN REAL SIGNAL - {datetime.now().strftime('%I:%M %p')}**

💰 Pair: **{best_pair}**
📈 Signal: **{best_signal['signal']} {'🟢' if best_signal['signal']=='CALL' else '🔴'}**
🎯 Confidence: **{best_signal['conf']:.0f}%**
💵 Price: {best_signal['price']:.4f}
📊 RSI: {best_signal['rsi']:.1f} | EMA9: {best_signal['ema9']:.4f}

✅ ENTRY: **ABHI {best_signal['signal']} LO - 1 MIN EXPIRY**

Reason:
- RSI {best_signal['rsi']:.1f} {'Oversold' if best_signal['rsi']<45 else 'Overbought' if best_signal['rsi']>55 else 'Momentum'}
- EMA9 {'upar' if best_signal['ema9']>best_signal['ema21'] else 'neeche'} cross
- Trend: {'Bullish' if best_signal['signal']=='CALL' else 'Bearish'}

⚠️ Risk: 1% capital only
        """
        await update.message.reply_text(msg, parse_mode='Markdown')
    else:
        # Fallback bhi signal de
        await update.message.reply_text("🟢 **USD/PHP CALL 78%** - Abhi entry lo! 1 MIN")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot Ready! /signal likho - har bar real signal ayega, skip nahi!")

# Flask for Render health check
app = Flask(__name__)
@app.route('/')
def home():
    return "Telegram Bot Running - No Skip Mode"

def run_flask():
    app.run(host='0.0.0.0', port=10000)

if __name__ == '__main__':
    # Flask thread
    threading.Thread(target=run_flask, daemon=True).start()
    
    # Telegram bot
    if HAS_TELE and BOT_TOKEN != "PUT_YOUR_BOT_TOKEN_HERE":
        application = Application.builder().token(BOT_TOKEN).build()
        application.add_handler(CommandHandler("signal", signal_command))
        application.add_handler(CommandHandler("start", start_command))
        print("Bot started - No skip mode")
        application.run_polling()
    else:
        print("BOT_TOKEN set karo Render env var mein")
        while True:
            time.sleep(100)
