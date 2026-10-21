import os
import sys
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is Live!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    # Flask ko background me chalao
    import threading
    threading.Thread(target=run_flask, daemon=True).start()
    
    print("Starting bot...", flush=True)
    try:
        import telebot
        TOKEN = os.getenv("BOT_TOKEN")
        print(f"Token found: {bool(TOKEN)}", flush=True)
        if not TOKEN:
            print("ERROR: BOT_TOKEN not set!", flush=True)
            sys.exit(1)
            
        bot = telebot.TeleBot(TOKEN)
        
        @bot.message_handler(commands=['start'])
        def start(m):
            bot.reply_to(m, "Bot Live Aqeel! ✅ Ab working hai!")

        print("Bot Polling Started ✅", flush=True)
        bot.infinity_polling()
    except Exception as e:
        print(f"BOT CRASH: {e}", flush=True)
