import os, time, threading, pytz, yfinance as yf, telebot
from flask import Flask
from datetime import datetime

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN, threaded=False)
app = Flask(__name__)

# PAIR + EXPIRY MAP
PAIRS = {
    "EUR/USD": {"sym": "EURUSD=X", "exp": "60 Sec (1 MIN)"},
    "GBP/USD": {"sym": "GBPUSD=X", "exp": "60 Sec (1 MIN)"},
    "USD/JPY": {"sym": "USDJPY=X", "exp": "120 Sec (2 MIN)"},
    "AUD/USD": {"sym": "AUDUSD=X", "exp": "60 Sec (1 MIN)"},
    "USD/CAD": {"sym": "CAD=X", "exp": "300 Sec (5 MIN)"},
    "GOLD": {"sym": "GC=F", "exp": "300 Sec (5 MIN) - BEST FOR NIGHT"}
}

def get_level(data):
    try:
        sym = data["sym"]
        exp = data["exp"]
        df = yf.download(sym, period="5d", interval="5m", progress=False, auto_adjust=True)
        if len(df) < 30: return None
        close = df['Close']
        ema9 = close.ewm(span=9).mean()
        ema21 = close.ewm(span=21).mean()
        delta = close.diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = -delta.where(delta < 0, 0).rolling(14).mean()
        rsi = 100 - (100 / (1 + gain/loss))
        price = float(close.iloc[-1])
        r9 = float(ema9.iloc[-1]); r21 = float(ema21.iloc[-1]); rsi_v = float(rsi.iloc[-1])
        
        if r9 > r21 and price > r9 and 38 < rsi_v < 68:
            return f"🟢 CALL (BUY)\n⏱ Expiry: {exp}\n📈 EMA 9({r9:.5f}) > 21({r21:.5f})\n📉 RSI: {rsi_v:.0f}"
        if r9 < r21 and price < r9 and 32 < rsi_v < 62:
            return f"🔴 PUT (SELL)\n⏱ Expiry: {exp}\n📈 EMA 9({r9:.5f}) < 21({r21:.5f})\n📉 RSI: {rsi_v:.0f}"
        return None
    except: return None

@bot.message_handler(commands=['start'])
def start(m): bot.reply_to(m, "✅ Kot Jamel Bot Ready!\n/pairs\n/signal\n/gold")

@bot.message_handler(commands=['pairs'])
def pairs_list(m):
    txt="📊 PAIR + EXPIRY LIST:\n\n"
    for k,v in PAIRS.items(): txt+=f"• {k} = {v['exp']}\n"
    txt+="\nBest Time: Subah 9 - Sham 6\nRaat ko GOLD use karo!"
    bot.reply_to(m, txt)

@bot.message_handler(commands=['signal'])
def sig(m):
    bot.send_message(m.chat.id, "🔍 1-MIN SCAN...")
    pkt = pytz.timezone('Asia/Karachi'); now = datetime.now(pkt)
    found=False
    for n,d in PAIRS.items():
        r=get_level(d)
        if r:
            bot.send_message(m.chat.id, f"🚨 {n}\n{r}\n🕒 {now.strftime('%I:%M %p')}")
            found=True; time.sleep(0.8)
    if not found:
        bot.send_message(m.chat.id, f"⏸️ Market Sideways Hai {now.strftime('%I:%M %p')}\nIs time koi clear trend nahi - Signal skip karna hi profit hai!\nBest: GOLD ya Subah try karo")

def run_bot():
    try: bot.delete_webhook(drop_pending_updates=True); time.sleep(1)
    except: pass
    while True:
        try: bot.infinity_polling(skip_pending=True, timeout=30)
        except: time.sleep(5)

@app.route('/')
def home(): return "Bot Running - Kot Jamel"
threading.Thread(target=run_bot, daemon=True).start()
if __name__ == "__main__": app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
