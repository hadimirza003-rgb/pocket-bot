import time
import telebot
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

# ==========================================
# 1. APNI DETAILS YAHAN CHANGE KAREIN
# ==========================================
TELEGRAM_TOKEN = "YAHAN_APNA_TELEGRAM_TOKEN_DALEIN"
CHAT_ID = "YAHAN_APNA_CHAT_ID_DALEIN"

# Telegram Bot Initialise
bot = telebot.TeleBot(TELEGRAM_TOKEN)
driver = None

def start_browser():
    """Browser open karne aur Pocket Option load karne ka function"""
    global driver
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get("https://pocketoption.com/")
    return driver

# ==========================================
# 2. TELEGRAM COMMANDS (IPHONE SE CONTROL)
# ==========================================

@bot.message_handler(commands=['start'])
def handle_start(message):
    msg = (
        "🤖 *Pocket Option Control Bot Connected!*\n\n"
        "Commands:\n"
        "🔹 /open_site - Pocket Option browser open karein\n"
        "🔹 /call - Higher (Green) Trade lagayein\n"
        "🔹 /put - Lower (Red) Trade lagayein\n"
        "🔹 /stop - Browser band karein"
    )
    bot.send_message(message.chat.id, msg, parse_mode="Markdown")

@bot.message_handler(commands=['open_site'])
def handle_open(message):
    bot.reply_to(message, "⏳ Pocket Option site open ho rahi hai... Computer me Login kar ke Demo Account select karein.")
    try:
        start_browser()
        bot.send_message(message.chat.id, "✅ Site open ho gayi! Ab aap phone se /call ya /put bhej kar trade laga sakte hain.")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Browser open nahi ho paya: {e}")

@bot.message_handler(commands=['call'])
def handle_call(message):
    global driver
    if not driver:
        bot.reply_to(message, "⚠️ Pehle /open_site bhej kar browser start karein!")
        return

    bot.reply_to(message, "📈 Executing CALL (Higher) Trade...")
    try:
        call_btn = driver.find_element(By.XPATH, "//button[contains(@class, 'btn-call') or contains(@class, 'call')]")
        call_btn.click()
        bot.send_message(message.chat.id, "✅ SUCCESS: CALL Trade lag gayi hai!")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Trade error (Button click fail): {e}")

@bot.message_handler(commands=['put'])
def handle_put(message):
    global driver
    if not driver:
        bot.reply_to(message, "⚠️ Pehle /open_site bhej kar browser start karein!")
        return

    bot.reply_to(message, "📉 Executing PUT (Lower) Trade...")
    try:
        put_btn = driver.find_element(By.XPATH, "//button[contains(@class, 'btn-put') or contains(@class, 'put')]")
        put_btn.click()
        bot.send_message(message.chat.id, "✅ SUCCESS: PUT Trade lag gayi hai!")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Trade error (Button click fail): {e}")

@bot.message_handler(commands=['stop'])
def handle_stop(message):
    global driver
    if driver:
        driver.quit()
        driver = None
        bot.reply_to(message, "🛑 Browser band kar diya gaya hai.")
    else:
        bot.reply_to(message, "⚠️ Koi active browser session nahi hai.")

# Bot Listener Start
if __name__ == "__main__":
    print("Bot is running... Control it from Telegram!")
    bot.polling(none_stop=True)
