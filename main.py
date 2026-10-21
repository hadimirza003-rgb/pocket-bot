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
        # ye line space ko khud kaat degi
        TOKEN = os.getenv("BOT_TOKEN", "").strip().replace(" ", "").replace("\n", "")
        print(f"Token check length: {len(TOKEN)}", flush=True)
        if not TOKEN:
            print("ERROR: BOT_TOKEN missing!", flush=True)
            return
        bot = telebot.TeleBot(TOKEN)
        
        @bot.message_handler(commands=['start'])
        def start(m):
            bot.reply_to(m, "Bot Live Aqeel! ✅")
        
        print("Bot Polling Started ✅", flush=True)
        bot.infinity_polling()
    except Exception as e:
        print(f"BOT CRASH: {e}", flush=True)

threading.Thread(target=run_bot, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
