import os, random, threading, time
from flask import Flask
import telebot
from datetime import datetime

app = Flask(__name__)
@app.route('/')
def home(): return "Bot Live with Signals!"

TOKEN = os.getenv("BOT_TOKEN", "").strip()
bot = telebot.TeleBot(TOKEN)

PAIRS = ["EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD", "EUR/GBP", "GOLD", "BTC/USD", "EUR/JPY"]

def get_signal():
    pair = random.choice(PAIRS)
    direction = random.choice(["BUY 🟢", "SELL 🔴"])
    tf = random.choice(["1 MIN", "2 MIN", "5 MIN"])
    now = datetime.now().strftime("%I:%M %p")
    return f"""
📊 **KOT JAMEL PRO SIGNAL**

💱 Pair: **{pair}**
📈 Signal: **{direction}**
⏱ Timeframe: {tf}
🕒 Time: {now}
⚡️ Validity: Next Candle

⚠️ Trade with Money Management!
@gpt_trade_pro_2028_bot
"""

@bot.message_handler(commands=['start'])
def start(m):
    bot.reply_to(m, "Welcome Aqeel! 🔥\n\nCommands:\n/signal - Get Signal\n/pairs - All Pairs\nBot is LIVE @gpt_trade_pro_2028_bot")

@bot.message_handler(commands=['signal'])
def signal(m):
    bot.reply_to(m, get_signal(), parse_mode="Markdown")

@bot.message_handler(commands=['pairs'])
def pairs(m):
    txt = "📋 Available Pairs:\n\n" + "\n".join([f"• {p}" for p in PAIRS])
    bot.reply_to(m, txt)

def run_bot():
    print("Bot Polling Started with Signals ✅", flush=True)
    bot.infinity_polling()

threading.Thread(target=run_bot, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
