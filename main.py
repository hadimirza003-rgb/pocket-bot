import os
from flask import Flask
import threading

app = Flask(__name__)
@app.route('/')
def home():
    return "Bot Live!"

def run_bot():
    try:
        import telebot
        raw = os.getenv("BOT_TOKEN","")
        TOKEN = raw.strip()  # <-- ye space khud kaat dega
        print(f"Raw token len: {len(raw)}, Stripped len: {len(TOKEN)}")
        if not TOKEN:
            print("BOT_TOKEN missing!")
            return
        bot = telebot.TeleBot(TOKEN)
        @bot.message_handler(commands=['start'])
        def start(m):
            bot.reply_to(m, "Bot Live Aqeel! ✅")
        print("Bot Polling Started ✅")
        bot.infinity_polling()
    except Exception as e:
        print(f"BOT CRASH: {e}")

threading.Thread(target=run_bot, daemon=True).start()
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT",10000)))
