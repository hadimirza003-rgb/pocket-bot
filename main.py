import os, time, threading, pytz, yfinance as yf, telebot, ta
from flask import Flask
from datetime import datetime
import pandas as pd

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN, threaded=False)
app = Flask(__name__)

PAIRS = {
    "EUR/USD": "EURUSD=X",
    "GBP/USD": "GBPUSD=X",
    "USD/JPY": "USDJPY=X",
    "AUD/USD": "AUDUSD=X",
    "GOLD": "GC=F"
}

def calculate_ta_signal(df):
    try:
        # ta library - tumhara wala logic
        df['ema_fast'] = ta.trend.EMAIndicator(df['Close'], window=9).ema_indicator()
        df['ema_slow'] = ta.trend.EMAIndicator(df['Close'], window=21).ema_indicator()
        df['rsi'] = ta.momentum.RSIIndicator(df['Close'], window=14).rsi()
        macd = ta.trend.MACD(df['Close'])
        df['macd'] = macd.macd()
        df['macd_signal'] = macd.macd_signal()
        
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        # CALL - BUY
        if (prev['ema_fast'] <= prev['ema_slow']) and (latest['ema_fast'] > latest['ema_slow']):
            if (40 < latest['rsi'] < 65) and (latest['macd'] > latest['macd_signal']):
                return f"🟢 CALL (BUY) | RSI:{latest['rsi']:.1f} | EMA Cross UP"
        
        # PUT - SELL
        if (prev['ema_fast'] >= prev['ema_slow']) and (latest['ema_fast'] < latest['ema_slow']):
            if (35 < latest['rsi'] < 60) and (latest['macd'] < latest['macd_signal']):
                return f"🔴 PUT (SELL) | RSI:{latest['rsi']:.1f} | EMA Cross DOWN"
        
        return None
    except Exception as e:
        print(f"TA Error: {e}")
        return None

def get_level(sym):
    try:
        # 1-MIN data - Pocket Option ke liye
        df = yf.download(sym, period="1d", interval="1m", progress=False, auto_adjust=True)
        if len(df) < 30:
            return None
        return calculate_ta_signal(df)
    except Exception as e:
        print(f"Err {sym}: {e}")
        return None

@bot.message_handler(commands=['start'])
def start(m):
    bot.reply_to(m, "✅ Kot Jamel 1-MIN BOT ONLINE\nEMA9/21 + RSI + MACD\n\n/pairs - List\n/signal - Scan\n/gold - Gold")

@bot.message_handler(commands=['pairs'])
def pairs_list(m):
    txt = "📊 1-MIN Pairs:\n"
    for k in PAIRS: txt+=f"• {k}\n"
    bot.reply_to(m, txt)

@bot.message_handler(commands=['signal'])
def sig(m):
    bot.send_message(m.chat.id, "🔍 1-MIN REAL SCAN...")
    pkt = pytz.timezone('Asia/Karachi')
    now = datetime.now(pkt)
    found=False
    for n,s in PAIRS.items():
        r=get_level(s)
        if r:
            bot.send_message(m.chat.id, f"🚨 {n}\n{r}\n⏱ 1 MIN Expiry\n{now.strftime('%I:%M %p')}")
            found=True
            time.sleep(1)
    if not found:
        bot.send_message(m.chat.id, f"⏳ No Signal Now - Market Searching\n{now.strftime('%I:%M %p')}\n2 min baad /signal")

@bot.message_handler(commands=['eurusd','gbpusd','usdjpy','audusd','gold'])
def single(m):
    cmd = m.text.replace('/','').upper()
    mp={"EURUSD":"EUR/USD","GBPUSD":"GBP/USD","USDJPY":"USD/JPY","AUDUSD":"AUD/USD","GOLD":"GOLD"}
    if cmd in mp:
        name=mp[cmd]
        r=get_level(PAIRS[name])
        bot.reply_to(m, f"{name} - {r if r else 'No Signal - Searching...'}")

def run_bot():
    try: bot.delete_webhook(drop_pending_updates=True); time.sleep(2)
    except: pass
    while True:
        try:
            print("Polling 1-MIN bot...")
            bot.infinity_polling(skip_pending=True, timeout=30)
        except Exception as e:
            print(f"Restart {e}"); time.sleep(5)

@app.route('/')
def home():
    return "Kot Jamel 1-MIN Bot Running"

threading.Thread(target=run_bot, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
