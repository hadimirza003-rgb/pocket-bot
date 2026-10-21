import os
from flask import Flask
import threading

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is Live!"

def run_bot():
    try:
        import telebot
        token = os.getenv("BOT_TOKEN")
        if not token:
            print("BOT_TOKEN missing!")
            return
        bot = telebot.TeleBot(token)

        @bot.message_handler(commands=['start'])
        def start(m):
            bot.reply_to(m, "Bot Live Aqeel! ✅ /start working!")

        print("Bot Polling Started ✅")
        bot.infinity_polling()
    except Exception as e:
        print(f"Bot Error: {e}")

threading.Thread(target=run_bot, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
