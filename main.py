import os, time, threading, pytz, yfinance as yf, telebot
from flask import Flask
from datetime import datetime

# --- TOKEN ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    print("ERROR: BOT_TOKEN not set!")
    
bot = telebot.TeleBot(BOT_TOKEN, threaded=False)
app = Flask(__name__)

PAIRS = {"EUR/USD":"EURUSD=X", "GBP/USD":"GBPUSD=X", "GOLD":"GC=F"}

def get_level(sym):
    try:
        df = yf.download(sym, period="1d", interval="5m", progress=False, auto_adjust=True)
        if len(df) < 50: return None
        df['EMA20'] = df['Close'].ewm(span=20).mean()
        delta = df['Close'].diff()
        gain = (delta.where(delta>0,0)).rolling(14).mean()
        loss = (-delta.where(delta<0,0)).rolling(14).mean()
        df['RSI'] = 100 - (100/(1+gain/loss))
        low = float(df['Low'][-20:].min())
        high = float(df['High'][-20:].max())
        price = float(df['Close'].iloc[-1])
        rsi = float(df['RSI'].iloc[-1])
        ema20 = float(df['EMA20'].iloc[-1])
        if price <= low*1.001 and rsi < 38 and price > ema20:
            return f"BUY LEVEL {low:.5f} RSI {rsi:.1f}"
        if price >= high*0.999 and rsi > 62 and price < ema20:
            return f"SELL LEVEL {high:.5f} RSI {rsi:.1f}"
        return None
    except:
        return None

@bot.message_handler(commands=['start'])
def start(m):
    bot.reply_to(m, "LEVEL BOT FIXED ✅\n/signal use karo")

@bot.message_handler(commands=['signal'])
def sig(m):
    bot.send_message(m.chat.id, "REAL SCAN...")
    found=False
    pkt = pytz.timezone('Asia/Karachi')
    now = datetime.now(pkt)
    for n,s in PAIRS.items():
        r=get_level(s)
        if r:
            bot.send_message(m.chat.id, f"{n} - {r}\n15M EXPIRY\n{now.strftime('%I:%M %p')}")
            found=True
    if not found:
        bot.send_message(m.chat.id, "No Level - 30 min baad try karo")

def run_bot():
    print("Bot Starting - Deleting webhook...")
    try:
        bot.delete_webhook(drop_pending_updates=True)
        time.sleep(3)
    except: pass
    while True:
        try:
            print("Polling started...")
            bot.infinity_polling(skip_pending=True, timeout=20, long_polling_timeout=20)
        except Exception as e:
            print(f"Bot error: {e} - restart 5s")
            time.sleep(5)

# Flask route for Render
@app.route('/')
def home():
    return "Bot Running - Kot Jamel Official"

# Start bot in thread
threading.Thread(target=run_bot, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
