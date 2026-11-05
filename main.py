import os
import telebot
from threading import Thread
from flask import Flask
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

TELEGRAM_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN_HERE"
CHAT_ID = "YOUR_CHAT_ID_HERE"

bot = telebot.TeleBot(TELEGRAM_TOKEN)
driver = None
app = Flask(__name__)

@app.route('/')
def home():
    return "Pocket Option Bot is Live!"

def run_telegram_bot():
    bot.infinity_polling()

@bot.message_handler(commands=['start'])
def handle_start(message):
    msg = (
        "🤖 *Pocket Option Bot Ready!*\n\n"
        "Commands:\n"
        "🔹 /open_site - Open Site\n"
        "🔹 /call - BUY (Green)\n"
        "🔹 /put - SELL (Red)\n"
        "🔹 /stop - Close Browser"
    )
    bot.send_message(message.chat.id, msg, parse_mode="Markdown")

@bot.message_handler(commands=['open_site'])
def handle_open(message):
    global driver
    bot.reply_to(message, "⏳ Opening Pocket Option in background...")
    try:
        options = Options()
        options.add_argument("--headless=new") # Render ke liye zaruri
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        
        # Render pe chromedriver pehle se hota hai
        driver = webdriver.Chrome(options=options)
        driver.get("https://pocketoption.com/en/cabinet/demo-quick-high-low/")
        bot.send_message(message.chat.id, "✅ Site Opened! Login kar lo aur /call /put use karo.")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")

@bot.message_handler(commands=['call'])
def handle_call(message):
    try:
        # Pocket Option ka real button
        btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a.btn-call, button.btn-call, .btn-call"))
        )
        btn.click()
        bot.send_message(message.chat.id, "✅ CALL (UP) Trade Done!")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ CALL Fail: {e}")

@bot.message_handler(commands=['put'])
def handle_put(message):
    try:
        btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a.btn-put, button.btn-put, .btn-put"))
        )
        btn.click()
        bot.send_message(message.chat.id, "✅ PUT (DOWN) Trade Done!")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ PUT Fail: {e}")

if __name__ == "__main__":
    Thread(target=run_telegram_bot, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
