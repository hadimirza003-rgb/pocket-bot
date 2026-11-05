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

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
CHAT_ID = os.environ.get("CHAT_ID", "")

if not TELEGRAM_TOKEN or ":" not in TELEGRAM_TOKEN:
    print("ERROR: TELEGRAM_TOKEN not set or invalid! Set it in Render Environment Variables")
    
bot = telebot.TeleBot(TELEGRAM_TOKEN) if TELEGRAM_TOKEN and ":" in TELEGRAM_TOKEN else None
driver = None
app = Flask(__name__)

@app.route('/')
def home():
    return "Pocket Option Bot is Live - OK!"

def run_telegram_bot():
    if not bot:
        print("Bot not started - invalid token")
        return
    print("Telegram Bot polling started...")
    bot.infinity_polling()

@bot.message_handler(commands=['start'])
def handle_start(message):
    if str(message.chat.id) != CHAT_ID and CHAT_ID != "":
        bot.reply_to(message, f"⛔ Unauthorized. Your ID: {message.chat.id}")
        return
    msg = (
        "🤖 *Pocket Option Control Bot Connected!*\n\n"
        "Available Commands:\n"
        "🔹 /open_site - Open Pocket Option browser\n"
        "🔹 /call - Execute Higher (Green) Trade\n"
        "🔹 /put - Execute Lower (Red) Trade\n"
        "🔹 /stop - Close the browser session"
    )
    bot.send_message(message.chat.id, msg, parse_mode="Markdown")

@bot.message_handler(commands=['open_site'])
def handle_open(message):
    global driver
    if str(message.chat.id) != CHAT_ID and CHAT_ID != "":
        return
    bot.reply_to(message, "⏳ Opening Pocket Option... Please wait 15-20 sec.")
    try:
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # Try to find chromium binary
        options.binary_location = "/usr/bin/chromium-browser" if os.path.exists("/usr/bin/chromium-browser") else "/usr/bin/chromium"
        
        driver = webdriver.Chrome(options=options)
        driver.get("https://pocketoption.com/en/cabinet/demo-quick-high-low/")
        bot.send_message(message.chat.id, "✅ Site opened! Now login in 1 min, then use /call or /put.")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Failed to open browser: {e}")
        print(f"Browser error: {e}")

@bot.message_handler(commands=['call'])
def handle_call(message):
    if not driver:
        bot.reply_to(message, "⚠️ Please send /open_site first!")
        return
    bot.reply_to(message, "📈 Executing CALL...")
    try:
        # Updated selectors for Pocket Option 2024/2025
        selectors = [
            "a.btn-call", "button.btn-call", ".btn-call",
            ".btn--call", "[data-action='call']",
            "//button[contains(text(),'Higher') or contains(text(),'Call')]",
        ]
        clicked = False
        for sel in selectors:
            try:
                if sel.startswith("//"):
                    btn = driver.find_element(By.XPATH, sel)
                else:
                    btn = driver.find_element(By.CSS_SELECTOR, sel)
                btn.click()
                clicked = True
                break
            except:
                continue
        if clicked:
            bot.send_message(message.chat.id, "✅ SUCCESS: CALL Trade placed!")
        else:
            bot.send_message(message.chat.id, "❌ Button not found - Please check if logged in")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Trade error: {e}")

@bot.message_handler(commands=['put'])
def handle_put(message):
    if not driver:
        bot.reply_to(message, "⚠️ Please send /open_site first!")
        return
    bot.reply_to(message, "📉 Executing PUT...")
    try:
        selectors = ["a.btn-put", "button.btn-put", ".btn-put", ".btn--put", "[data-action='put']"]
        clicked = False
        for sel in selectors:
            try:
                btn = driver.find_element(By.CSS_SELECTOR, sel)
                btn.click()
                clicked=True
                break
            except:
                continue
        if clicked:
            bot.send_message(message.chat.id, "✅ SUCCESS: PUT Trade placed!")
        else:
            bot.send_message(message.chat.id, "❌ Button not found")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Trade error: {e}")

@bot.message_handler(commands=['stop'])
def handle_stop(message):
    global driver
    if driver:
        driver.quit()
        driver = None
        bot.reply_to(message, "🛑 Browser closed.")
    else:
        bot.reply_to(message, "⚠️ No active session.")

if __name__ == "__main__":
    if bot:
        t = Thread(target=run_telegram_bot)
        t.daemon = True
        t.start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
