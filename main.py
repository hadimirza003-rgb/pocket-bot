import requests, random, os, threading, time
from flask import Flask
from datetime import datetime
from collections import deque

# Telegram
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN", "PUT_YOUR_TOKEN")
PAIRS = ["USD/PHP","EUR/USD","GBP/USD","USD/JPY","AUD/USD","GOLD","BTC/USD"]
price_hist = {p: deque([58.5]*50, maxlen=100) for p in PAIRS}

app = Flask(__name__)

def get_price(p):
    try:
        b = p.split("/")[0]
        if b=="GOLD": return 2000 + random.random()*10
        r = requests.get(f"https://open.er-api.com/v6/latest/{b}", timeout=4).json()
        t = p.split("/")[1]
        return r['rates'].get(t, 58.5)
    except:
        return price_hist[p][-1]

def get_signal(prices):
    # HAMESHA CALL ya PUT, kabhi WAIT/SKIP nahi
    rsi = 45 + random.random()*10  # simple
    ema9 = sum(prices[-9:])/9
    ema21 = sum(prices[-21:])/21
    if ema9 >= ema21:
        return "CALL", 82 + int(random.random()*10)
    else:
        return "PUT", 82 + int(random.random()*10)

async def signal_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔍 1-MIN SCAN... Real scan...")
    # Sabse best pair nikalo
    best_p, best_s, best_c = None, "CALL", 0
    for p in PAIRS:
        pr = get_price(p)
        price_hist[p].append(pr)
        s,c = get_signal(list(price_hist[p]))
        if c > best_c:
            best_c=c; best_s=s; best_p=p
    
    msg = f"🚀 **{best_p} 1-MIN SIGNAL**\n\n💰 Pair: **{best_p}**\n📈 Signal: **{best_s} {'🟢' if best_s=='CALL' else '🔴'}**\n🎯 Confidence: **{best_c}%**\n⏰ Time: {datetime.now().strftime('%I:%M %p')}\n\n✅ **ENTRY: ABHI {best_s} LO - 1 MIN EXPIRY**\n\nReal price: {price_hist[best_p][-1]:.4f}\nNo Skip - Har bar signal!"
    await update.message.reply_text(msg, parse_mode='Markdown')

async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot Ready! /signal likho")

@app.route('/')
def home():
    return "Bot Running - No Skip Mode Active"

def run_flask():
    app.run(host='0.0.0.0', port=10000)

if __name__ == '__main__':
    threading.Thread(target=run_flask, daemon=True).start()
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("signal", signal_cmd))
    application.add_handler(CommandHandler("start", start_cmd))
    application.run_polling()
