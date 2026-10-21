import os, time, threading, pytz, yfinance as yf, telebot
from flask import Flask
from datetime import datetime
import pandas as pd

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN, threaded=False)
app = Flask(__name__)

PAIRS = {"EUR/USD":"EURUSD=X", "GBP/USD":"GBPUSD=X", "USD/JPY":"JPY=X", "GOLD":"GC=F"}

def get_level(sym):
    try:
        df = yf.download(sym, period="1d", interval="5m", progress=False, auto_adjust=True)
        if len(df) < 30:
            return None
        
        close = df['Close']
        # Safe RSI
        delta = close.diff()
        gain = delta.where(delta > 0, 0).rolling(window=14).mean()
        loss = -delta.where(delta < 0, 0).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        ema20 = close.ewm(span=20).mean()
        
        price = float(close.iloc[-1])
        rsi_val = float(rsi.iloc[-1])
        ema_val = float(ema20.iloc[-1])
        
        low_20 = float(df['Low'][-20:].min())
        high_20 = float(df['High'][-20:].max())
        
        # Simple but strong
        if price <= low_20*1.002 and rsi_val < 40 and price > ema_val:
            return f"BUY LEVEL {low_20:.5f} | RSI {rsi_val:.0f}"
        if price >= high_20*0.998 and rsi_val > 60 and price < ema_val:
            return f"SELL LEVEL {high_20:.5f} | RSI {rsi_val:.0f}"
        return None
    except Exception as e:
        print(f"Error {sym}: {e}")
        return None

@bot.message_handler(commands=['start'])
def start(m):
    bot.reply_to(m, "✅ Kot Jamel Bot ONLINE\n/signal bhejo")

@bot.message_handler(commands=['signal'])
def sig(m):
    bot.send_message(m.chat.id, "REAL SCAN...")
    pkt = pytz.timezone('Asia/Karachi')
    now = datetime.now(pkt)
    found=False
    for n,s in PAIRS.items():
        r=get_level(s)
        if r:
            bot.send_message(m.chat.id, f"{n} - {r}\n⏰ 15M Expiry\n{now.strftime('%I:%M %p')}")
            found=True
    if not found:
        bot.send_message(m.chat.id, "No Level - 30 min baad try karo")

@bot.message_handler(commands=['pairs'])
def pairs(m):
    bot.reply_to(m, "Pairs: EUR/USD, GBP/USD, USD/JPY, GOLD")

def run_bot():
    try:
        bot.delete_webhook(drop_pending_updates=True)
        time.sleep(2)
    except: pass
    while True:
        try:
            print("Polling started...")
            bot.infinity_polling(skip_pending=True, timeout=30)
        except Exception as e:
            print(f"Restart: {e}")
            time.sleep(5)

@app.route('/')
def home():
    return "Bot Running - Kot Jamel Official"

threading.Thread(target=run_bot, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
