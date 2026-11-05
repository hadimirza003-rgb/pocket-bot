import os
import time
import threading
import pandas as pd
import yfinance as yf
from flask import Flask, jsonify
from datetime import datetime
import telebot

# Telegram Bot Setup (Apna Token aur Chat ID yahan daalein)
TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
CHAT_ID = "YOUR_TELEGRAM_CHAT_ID"
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)

PAIRS = {
    "EUR/USD": "EURUSD=X",
    "GBP/USD": "GBPUSD=X"
}

@app.route('/')
def home():
    return "Pocket Option Telegram Signal Bot is Running Successfully!"

def send_telegram_message(message):
    try:
        bot.send_message(CHAT_ID, message, parse_mode="Markdown")
    except Exception as e:
        print(f"Telegram Error: {e}")

def signal_generator():
    print("Signal Generator Thread Started...")
    while True:
        try:
            for pair_name, ticker in PAIRS.items():
                # Yahoo Finance se data download karna
                df = yf.download(ticker, period="2d", interval="1m", progress=False)
                
                if df.empty or len(df) < 20:
                    continue
                
                # Simple logic for signal generation (CALL/PUT)
                close_price = df['Close'].iloc[-1]
                prev_price = df['Close'].iloc[-2]
                
                if isinstance(close_price, pd.Series):
                    close_price = close_price.iloc[0]
                    prev_price = prev_price.iloc[0]

                action = "CALL (UP) 🟢" if close_price > prev_price else "PUT (DOWN) 🔴"
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                msg = f"""
🚨 **Pocket Option Signal** 🚨
📊 **Pair:** {pair_name}
⚡ **Action:** {action}
🕒 **Time:** {current_time}
                """
                
                # Telegram par message bhejna
                send_telegram_message(msg)
                print(f"Signal sent for {pair_name}")
                
            # Har 5 minute me naya signal check karega
            time.sleep(300)
            
        except Exception as e:
            print(f"Error in signal loop: {e}")
            time.sleep(60)

if __name__ == "__main__":
    # Background thread me signal generator chalana taaki Render ka web server active rahe
    t = threading.Thread(target=signal_generator)
    t.daemon = True
    t.start()
    
    # Flask app ko run karna (Render ke liye zaroori hai)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
