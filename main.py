import os, time, pytz, yfinance as yf
import telebot
from datetime import datetime

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN, threaded=False)

PAIRS = {
    "EUR/USD": "EURUSD=X",
    "GBP/USD": "GBPUSD=X",
    "GOLD": "GC=F"
}

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
            return f"BUY LEVEL Support {low:.5f} RSI {rsi:.1f}"
        if price >= high*0.999 and rsi > 62 and price < ema20:
            return f"SELL LEVEL Resistance {high:.5f} RSI {rsi:.1f}"
        return None
    except:
        return None

@bot.message_handler(commands=['start'])
def start(m):
    bot.reply_to(m, "LEVEL BOT FIXED ✅\nUse /signal")

@bot.message_handler(commands=['signal'])
def sig(m):
    pkt = pytz.timezone('Asia/Karachi')
    now = datetime.now(pkt)
    if now.hour >=22 or now.hour <=7:
        bot.reply_to(m, "SLEEP 10pm-8am PKT")
        return
    bot.send_message(m.chat.id, "SCAN REAL MARKET...")
    found=False
    for n,s in PAIRS.items():
        r=get_level(s)
        if r:
            bot.send_message(m.chat.id, f"{n} - {r}\nEXPIRY 15M\n{now.strftime('%I:%M %p')}")
            found=True
    if not found:
        bot.send_message(m.chat.id, "No Level - Wait 30 min")

# ---- 409 FIX ----
if __name__ == "__main__":
    print("Starting bot - fixing 409...")
    try:
        bot.delete_webhook(drop_pending_updates=True)
        print("Webhook deleted")
        time.sleep(3)
    except Exception as e:
        print(f"Webhook error: {e}")

    while True:
        try:
            print("Polling started...")
            bot.infinity_polling(skip_pending=True, timeout=20, long_polling_timeout=20)
        except Exception as e:
            print(f"Polling error: {e} - restarting in 5s")
            time.sleep(5)
