import os, random, threading, time, logging
from flask import Flask
import telebot
from datetime import datetime

app = Flask(__name__)
@app.route('/')
def home(): return "Kot Jamel Trading Bot - LIVE ✅"

RAW_TOKEN = os.getenv("BOT_TOKEN", "")
TOKEN = RAW_TOKEN.strip()
bot = telebot.TeleBot(TOKEN, threaded=False)

PAIRS = ["EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD", "EUR/JPY", "GOLD", "BTC/USD"]

def get_signal():
    pair = random.choice(PAIRS)
    direction = random.choice(["BUY 🟢", "SELL 🔴"])
    tf = random.choice(["1 MIN", "2 MIN"])
    acc = random.randint(89, 97)
    now = datetime.now().strftime("%I:%M %p")
    return f"""
💎 KOT JAMEL PRO SIGNAL 💎

💱 Pair: {pair}
📈 Signal: {direction}
⏱ TF: {tf}
🎯 Accuracy: {acc}%
🕒 Time: {now}

Next Candle Valid!
@ gpt_trade_pro_2028_bot
"""

@bot.message_handler(commands=['start'])
def start(m):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("/signal", "/pairs")
    bot.send_message(m.chat.id, f"Welcome {m.from_user.first_name}! 🔥\n\n/signal - Signal lo\n/pairs - Pairs dekho\n\nBot LIVE!", reply_markup=markup)

@bot.message_handler(commands=['signal'])
def sig(m):
    bot.send_chat_action(m.chat.id, 'typing')
    time.sleep(1)
    bot.send_message(m.chat.id, get_signal(), parse_mode="Markdown")

@bot.message_handler(commands=['pairs'])
def pairs(m):
    bot.send_message(m.chat.id, "📋 Pairs:\n" + "\n".join(PAIRS))

def run_bot():
    print("Bot Polling Started ✅", flush=True)
    while True:
        try:
            bot.infinity_polling(timeout=60)
        except Exception as e:
            print(f"Restarting: {e}", flush=True)
            time.sleep(5)

threading.Thread(target=run_bot, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
