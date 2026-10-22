import yfinance as yf
import telebot, os, time, pytz
from datetime import datetime

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

PAIRS = {
    "EUR/USD": "EURUSD=X",
    "GBP/USD": "GBPUSD=X", 
    "USD/JPY": "JPY=X",
    "GOLD": "GC=F",
    "BTC/USD": "BTC-USD"
}

def get_signal(sym):
    df = yf.download(sym, period="5d", interval="15m", progress=False, auto_adjust=True)
    if len(df) < 50: return None
    close = df['Close']
    if hasattr(close, 'iloc'): close = close.iloc[:,0] if len(close.shape)>1 else close
    ema20 = close.ewm(span=20).mean()
    ema50 = close.ewm(span=50).mean()
    delta = close.diff()
    gain = delta.where(delta>0,0).ewm(alpha=1/14).mean()
    loss = (-delta.where(delta<0,0)).ewm(alpha=1/14).mean()
    rsi = 100 - (100/(1+gain/loss))
    price = float(close.iloc[-1])
    r20 = float(rsi.iloc[-1])
    e20 = float(ema20.iloc[-1])
    e50 = float(ema50.iloc[-1])
    pe20 = float(ema20.iloc[-2])
    pe50 = float(ema50.iloc[-2])

    if pe20 < pe50 and e20 > e50: return f"BUY - Price {price:.5f} RSI {r20:.1f}"
    if pe20 > pe50 and e20 < e50: return f"SELL - Price {price:.5f} RSI {r20:.1f}"
    return None

@bot.message_handler(commands=['signal'])
def sig(m):
    bot.send_message(m.chat.id, "📡 SCANNING 5 PAIRS...")
    found=False
    for name,sym in PAIRS.items():
        res=get_signal(sym)
        if res:
            bot.send_message(m.chat.id, f"🎯 {name} - {res}\n⏰ 15M Expiry")
            found=True
            time.sleep(1)
    if not found:
        bot.send_message(m.chat.id, "⏳ Abhi koi strong signal nahi - 15 min baad /signal likho")

@bot.message_handler(commands=['start'])
def st(m):
    bot.reply_to(m, "Bot Ready! /signal likho")

while True:
    try:
        bot.infinity_polling()
    except:
        time.sleep(5)
