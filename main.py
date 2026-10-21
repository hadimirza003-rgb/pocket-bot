import os, time, threading, pytz, yfinance as yf, telebot
from flask import Flask
from datetime import datetime

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    print("BOT_TOKEN missing!")

bot = telebot.TeleBot(BOT_TOKEN, threaded=False)
app = Flask(__name__)

# --- CORRECT PAIRS FOR 【entity-YAHOO¦canonical_name=YAHOO】 ---
PAIRS = {
    "EUR/USD": "EURUSD=X",
    "GBP/USD": "GBPUSD=X",
    "USD/JPY": "USDJPY=X",
    "AUD/USD": "AUDUSD=X",
    "USD/CAD": "CAD=X",
    "GOLD": "GC=F"
}

def get_level(sym):
    try:
        df = yf.download(sym, period="1d", interval="5m", progress=False, auto_adjust=True)
        if len(df) < 20:
            return None
        close = df['Close']
        delta = close.diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = -delta.where(delta < 0, 0).rolling(14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        price = float(close.iloc[-1])
        rsi_val = float(rsi.iloc[-1])
        low_20 = float(df['Low'][-20:].min())
        high_20 = float(df['High'][-20:].max())
        
        # ALL SET - Sensitive settings taake signal aaye
        if price <= low_20 * 1.005 and rsi_val < 48:
            return f"BUY ✅ {low_20:.5f} RSI:{rsi_val:.0f}"
        if price >= high_20 * 0.995 and rsi_val > 52:
            return f"SELL ✅ {high_20:.5f} RSI:{rsi_val:.0f}"
        return None
    except Exception as e:
        print(f"Err {sym}: {e}")
        return None

@bot.message_handler(commands=['start'])
def start(m):
    bot.reply_to(m, "✅ Kot Jamel Bot ONLINE - All Set!\n\n/pairs - Pairs List\n/signal - All Scan\n/eurusd - Single Pair")

@bot.message_handler(commands=['pairs'])
def pairs_list(m):
    txt = "📊 Pairs:\n"
    for k in PAIRS.keys():
        txt += f"• {k}\n"
    txt += "\nUse /signal"
    bot.reply_to(m, txt)

@bot.message_handler(commands=['eurusd', 'gbpusd', 'usdjpy', 'audusd', 'usdcad', 'gold'])
def single(m):
    cmd = m.text.replace('/','').upper()
    mp = {"EURUSD":"EUR/USD","GBPUSD":"GBP/USD","USDJPY":"USD/JPY","AUDUSD":"AUD/USD","USDCAD":"USD/CAD","GOLD":"GOLD"}
    if cmd in mp:
        name = mp[cmd]
        r = get_level(PAIRS[name])
        if r:
            bot.reply_to(m, f"{name} - {r}")
        else:
            bot.reply_to(m, f"{name} - No Level - Try after 15m")

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
            time.sleep(1)
    if not found:
        bot.send_message(m.chat.id, f"No Level now ({now.strftime('%I:%M %p')}) - 15m baad try karo")

def run_bot():
    try:
        bot.delete_webhook(drop_pending_updates=True)
        time.sleep(2)
    except: pass
    while True:
        try:
            print("Polling started - All Set!")
            bot.infinity_polling(skip_pending=True, timeout=30)
        except Exception as e:
            print(f"Restart: {e}")
            time.sleep(5)

@app.route('/')
def home():
    return "Bot Running - Kot Jamel Official - ALL SET"

threading.Thread(target=run_bot, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
