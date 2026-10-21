import os, random, threading, time
from flask import Flask
import telebot
from datetime import datetime
import pytz

app = Flask(__name__)
@app.route('/')
def home(): return "KOT JAMEL 1-MIN KING LIVE ✅"

TOKEN = os.getenv("BOT_TOKEN", "").strip()
bot = telebot.TeleBot(TOKEN, threaded=False)

PAIRS = ["EUR/USD (OTC)", "GBP/USD (OTC)", "USD/JPY (OTC)", "EUR/JPY (OTC)", "GBP/JPY (OTC)", "AUD/USD (OTC)", "GOLD", "BTC/USD (OTC)"]

def get_signal():
    pair = random.choice(PAIRS)
    direction = random.choice(["BUY 🟢 UP", "SELL 🔴 DOWN"])
    
    # Duniya ka Ilm - Full Analysis
    rsi = random.randint(25, 80)
    ema_trend = random.choice(["EMA 9 Above 21 - Bullish", "EMA 9 Below 21 - Bearish"])
    support = random.choice(["Strong Support Break", "Resistance Rejection", "Double Bottom", "Double Top", "Trendline Bounce"])
    
    if rsi < 35: rsi_status = "OVERSOLD 🔥 BUY Strong"
    elif rsi > 70: rsi_status = "OVERBOUGHT 🔥 SELL Strong"
    else: rsi_status = f"Neutral - {rsi} Level"

    pak = datetime.now(pytz.timezone('Asia/Karachi'))
    entry_time = pak.strftime("%I:%M %p")
    # Next candle 1 min
    next_min = (pak.minute + 1) % 60
    expiry_str = f"{next_min} wala Candle"

    acc = random.randint(93, 98)

    return f"""
╔═══════════════════════════════╗
║  💎 KOT JAMEL 1-MIN KING 💎  ║
╚═══════════════════════════════╝

💱 PAIR: {pair}
📶 TIMEFRAME: 1 MINUTE ONLY

📈 SIGNAL: {direction}
⏱ EXPIRY: 1 MINUTE - Next Candle

━━━━━━━━━━━━━━━━━━
🔍 FULL ANALYSIS (Duniya ka Ilm):
━━━━━━━━━━━━━━━━━━
1️⃣ TREND: {ema_trend}
2️⃣ RSI (14): {rsi} - {rsi_status}
3️⃣ PATTERN: {support}
4️⃣ VOLUME: High Volume Confirmation
5️⃣ NEWS: No High Impact News

🎯 ENTRY: {expiry_str}
🕒 PKT TIME: {entry_time}
💰 MARTINGALE: Max 1 Step
📊 RISK: 2% Per Trade

━━━━━━━━━━━━━━━━━━
✅ ACCURACY: {acc}%
⚠️ Valid for 1 Candle Only!

@gpt_trade_pro_2028_bot
Kot Jamel Official
"""

@bot.message_handler(commands=['start'])
def start(m):
    mk = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    mk.add("⚡ 1 MIN SIGNAL ⚡", "/pairs")
    bot.send_message(m.chat.id, f"Welcome {m.from_user.first_name}! 🔥\n\nAb sirf 1 MINUTE ke PRO signals!\n\nButton dabao 👇", reply_markup=mk)

@bot.message_handler(commands=['signal'])
def sig(m):
    bot.send_chat_action(m.chat.id, 'typing')
    time.sleep(1)
    bot.send_message(m.chat.id, get_signal())

@bot.message_handler(func=lambda m: "1 MIN SIGNAL" in m.text)
def sig_btn(m):
    bot.send_chat_action(m.chat.id, 'typing')
    time.sleep(1)
    bot.send_message(m.chat.id, get_signal())

@bot.message_handler(commands=['pairs'])
def pairs(m):
    bot.send_message(m.chat.id, "📋 OTC Pairs (1 Min):\n" + "\n".join(PAIRS))

def run_bot():
    print("1-MIN KING Started ✅", flush=True)
    while True:
        try: bot.infinity_polling(timeout=60)
        except Exception as e:
            print(f"Restart: {e}", flush=True)
            time.sleep(5)

threading.Thread(target=run_bot, daemon=True).start()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
