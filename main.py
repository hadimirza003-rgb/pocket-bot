import os, random, datetime
import telebot
from threading import Thread
from flask import Flask

TOKEN = os.environ.get("TELEGRAM_TOKEN") or os.environ.get("BOT_TOKEN") or ""
print(f"Starting with token present: {bool(TOKEN)}")

if not TOKEN or ":" not in TOKEN:
    print("ERROR: TELEGRAM_TOKEN/BOT_TOKEN not set or invalid!")
    bot = None
else:
    bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)

@app.route('/')
def home():
    return "GPT Trade Pro Bot is Live - OK!"

def run_telegram_bot():
    if not bot:
        return
    print("Telegram Bot polling started...")
    bot.infinity_polling()

PAIRS = [
    "EUR/USD OTC","GBP/USD OTC","USD/JPY OTC","EUR/JPY OTC",
    "AUD/USD OTC","USD/CAD OTC","GBP/JPY OTC","EUR/GBP OTC",
    "EUR/AUD OTC","USD/CHF OTC","AUD/JPY OTC","NZD/USD OTC",
    "EUR/CAD OTC","GBP/CAD OTC","BTC/USD OTC","ETH/USD OTC",
    "EUR/USD","GBP/USD","USD/JPY"
]

def generate_signal():
    pair = random.choice(PAIRS)
    action = random.choice(["CALL 🔼", "PUT 🔽"])
    now = datetime.datetime.now().strftime("%H:%M")
    expiry = (datetime.datetime.now() + datetime.timedelta(minutes=2)).strftime("%H:%M")
    confidence = random.randint(78, 94)
    return (
        f"⚡️ *GPT TRADE PRO SIGNAL* ⚡️\n\n"
        f"📊 Pair: *{pair}*\n"
        f"📈 Action: *{action}*\n"
        f"⏱️ Time: *1 MIN*\n"
        f"🕒 Entry: {now} - Expiry: {expiry}\n"
        f"✅ Confidence: *{confidence}%*\n\n"
        f"⚠️ Risk: 1-2% balance\n"
        f"_Valid for next 1 minute_"
    )

@bot.message_handler(commands=['start'])
def start(m):
    bot.send_message(m.chat.id,
        "🤖 *GPT TRADE PRO 2028 Bot Connected!* 🚀\n\n"
        "Commands:\n"
        "⚡️ /signal - Get new signal\n"
        "⚡️ SIGNAL LO - Quick signal\n"
        "📊 /pairs - All pairs\n"
        "🔄 /restart - Restart bot",
        parse_mode="Markdown")

@bot.message_handler(commands=['signal','signals'])
def signal_cmd(m):
    bot.send_message(m.chat.id, generate_signal(), parse_mode="Markdown")

@bot.message_handler(func=lambda msg: msg.text and "SIGNAL LO" in msg.text.upper())
def signal_lo(m):
    bot.send_message(m.chat.id, generate_signal(), parse_mode="Markdown")

@bot.message_handler(commands=['pairs'])
def pairs_cmd(m):
    txt = "📊 *Available Pairs:*\n\n" + "\n".join([f"• {p}" for p in PAIRS])
    bot.send_message(m.chat.id, txt, parse_mode="Markdown")

@bot.message_handler(commands=['restart'])
def restart_cmd(m):
    bot.send_message(m.chat.id, "🔄 Bot Ready! Send /signal")

@bot.message_handler(commands=['call','put'])
def call_put(m):
    action = "CALL 🔼" if "call" in m.text.lower() else "PUT 🔽"
    bot.send_message(m.chat.id, f"✅ {action} Executed!")

if __name__ == "__main__":
    if bot:
        t = Thread(target=run_telegram_bot)
        t.daemon = True
        t.start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
