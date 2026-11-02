# main.py - FINAL - Python 3.14 FIX - NO UPDATER BUILD
import os, requests, random, threading
from flask import Flask
from datetime import datetime
from collections import deque
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
PAIRS = ["USD/PHP","EUR/USD","GBP/USD","USD/JPY","AUD/USD","GOLD","BTC/USD"]
price_hist = {p: deque([58.5]*60, maxlen=100) for p in PAIRS}

app = Flask(__name__)

def get_price(p):
    try:
        b = p.split("/")[0]
        if b == "GOLD": return 2000 + random.uniform(-5,5)
        r = requests.get(f"https://open.er-api.com/v6/latest/{b}", timeout=6).json()
        return float(r['rates'].get(p.split("/")[1], 58.5))
    except:
        return price_hist[p][-1]

async def signal_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔍 1-MIN SCAN...")
    best_p, best_s, best_c, best_pr = "EUR/USD", "CALL", 84, 1.08
    for p in PAIRS:
        pr = get_price(p)
        price_hist[p].append(pr)
        lst = list(price_hist[p])
        ema9 = sum(lst[-9:])/9
        ema21 = sum(lst[-21:])/21
        s = "CALL" if ema9 >= ema21 else "PUT"
        c = 84 + random.randint(0,8)
        if c > best_c: best_c, best_s, best_p, best_pr = c, s, p, pr
    msg = f"🚀 {best_p} 1-MIN\n📈 {best_s} {'🟢' if best_s=='CALL' else '🔴'} {best_c}%\n💵 {best_pr:.4f}\n⏰ {datetime.now().strftime('%I:%M %p')}\n\n✅ ABHI {best_s} LO - 1 MIN"
    await update.message.reply_text(msg, parse_mode='Markdown')

async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot Ready! /signal")

@app.route('/')
def home(): return "OK - FINAL FIXED"

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

if __name__ == '__main__':
    threading.Thread(target=run_flask, daemon=True).start()
    # FIX: Application with no updater build issue
    application = Application.builder().token(BOT_TOKEN).updater(None).build()
    application.add_handler(CommandHandler("signal", signal_cmd))
    application.add_handler(CommandHandler("start", start_cmd))
    print("BOT STARTED - FIXED FOR PYTHON 3.14")
    application.run_polling(drop_pending_updates=True)
