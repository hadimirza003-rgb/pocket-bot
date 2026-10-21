import yfinance as yf
import telebot, os, time, pytz
from datetime import datetime

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

PAIRS = {
    "EUR/USD": "EURUSD=X",
    "GBP/USD": "GBPUSD=X", 
    "USD/JPY": "JPY=X",
    "GOLD": "GC=F"
}

def get_level_signal(sym):
    try:
        df = yf.download(sym, period="1d", interval="5m", progress=False, auto_adjust=True)
        if len(df) < 60: return None
        df['EMA20'] = df['Close'].ewm(span=20).mean()
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        low = float(df['Low'][-20:].min())
        high = float(df['High'][-20:].max())
        price = float(df['Close'].iloc[-1])
        rsi = float(df['RSI'].iloc[-1])
        ema20 = float(df['EMA20'].iloc[-1])
        if price <= low * 1.001 and rsi < 38 and price > ema20:
            return "BUY LEVEL", f"Support {low:.5f}", rsi
        if price >= high * 0.999 and rsi > 62 and price < ema20:
            return "SELL LEVEL", f"Resistance {high:.5f}", rsi
        return None
    except:
        return None

@bot.message_handler(commands=['signal'])
def signal_cmd(m):
    pkt = pytz.timezone('Asia/Karachi')
    now = datetime.now(pkt)
    if now.hour >= 22 or now.hour <= 7:
        bot.reply_to(m, "SLEEP MODE 10pm-8am PKT")
        return
    bot.send_message(m.chat.id, "REAL LEVEL SCAN...")
    found=False
    for name, sym in PAIRS.items():
        res=get_level_signal(sym)
        if res:
            sig, level, rsi=res
            bot.send_message(m.chat.id, f"{name} - {sig}\n{level}\nRSI {rsi:.1f}\nEXPIRY 15M\n{now.strftime('%I:%M %p')}\nDEMO ONLY")
            found=True
    if not found:
        bot.send_message(m.chat.id, "No LEVEL - Wait 30 min")

@bot.message_handler(commands=['start'])
def start_cmd(m):
    bot.reply_to(m, "LEVEL BOT READY - Use /signal")

def run():
    try: bot.remove_webhook()
    except: pass
    while True:
        try:
            bot.infinity_polling()
        except:
            time.sleep(5)
run()
