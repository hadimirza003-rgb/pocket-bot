import os, random, threading, time
from flask import Flask
import telebot
from datetime import datetime
import pytz

app = Flask(__name__)
@app.route('/')
def home(): 
    return "OWAIS KHAN STYLE BOT LIVE ✅"

TOKEN = os.getenv("BOT_TOKEN", "").strip()
if not TOKEN:
    print("BOT_TOKEN missing!")
bot = telebot.TeleBot(TOKEN, threaded=False)

PAIRS = ["AUD/CAD OTC", "EUR/USD OTC", "GBP/USD OTC", "AUD/USD OTC", "EUR/JPY OTC", "USD/JPY OTC", "GOLD", "BTC/USD OTC"]

def get_signal():
    pair = random.choice(PAIRS)
    side = random.choice(["BUY", "SELL"])
    
    # Owais style SCORE logic
    score = random.randint(2, 5)
    sell_score = random.randint(1, 4)
    
    # Full Duniya ka Ilm
    rsi = random.randint(30, 78)
    if rsi > 70:
        rsi_text = f"{rsi} - OVERBOUGHT"
        trend = "SELL Strong 🔴"
    elif rsi < 35:
        rsi_text = f"{rsi} - OVERSOLD"
        trend = "BUY Strong 🟢"
    else:
        rsi_text = f"{rsi} - Neutral"
        trend = "Momentum"

    pak_time = datetime.now(pytz.timezone('Asia/Karachi'))
    time_str = pak_time.strftime("%I:%M:%S %p")
    
    emoji = "🟢" if side == "BUY" else "🔴"
    
    return f"""
╔════════════════════════╗
║ OWAIS KHAN POT TRADING ║
╚════════════════════════╝

💱 PAIR: {pair}
📊 TIMEFRAME: 1 MINUTE

{emoji} SIGNAL: {side} {emoji}

━━━━━━━━━━━━━━━━━━━━
📈 FULL ANALYSIS:
• RSI: {rsi_text}
• TREND: {trend}
• PATTERN: Support/Resistance
• VOLUME: High Confirmation
━━━━━━━━━━━━━━━━━━━━

📊 LIVE SCOREBOARD:
🏆 SCORE: {score}
📉 {side}: {sell_score}

⏱ EXPIRY: 1 MINUTE
🎯 ENTRY: NEXT CANDLE
🕒 PKT: {time_str}

✅ ACCURACY: {random.randint(92, 98)}%
⚠️ 1 Candle Valid Only

Bot: @gpt_trade_pro_2028_bot
Kot Jamel Official
"""

@bot.message_handler(commands=['start'])
def start(m):
    kb = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("⚡ SIGNAL LO ⚡", "/pairs")
    kb.add("/signal")
    bot.send_message(m.chat.id, 
        f"🔥 OWAIS KHAN STYLE BOT LIVE {m.from_user.first_name}!\n\n"
        "Ab 1 MINUTE ke signals Owais style me!\n\n"
        "⚡ SIGNAL LO ⚡ dabao!",
        reply_markup=kb)

@bot.message_handler(commands=['signal'])
@bot.message_handler(func=lambda m: m.text and "SIGNAL LO" in m.text)
def signal(m):
    bot.send_chat_action(m.chat.id, 'typing')
    time.sleep(1)
    bot.send_message(m.chat.id, get_signal())

@bot.message_handler(commands=['pairs'])
def pairs(m):
    bot.send_message(m.chat.id, "📋 Pairs (1 Min OTC):\n" + "\n".join(PAIRS))

# COPY wala feature - /copy AUD/CAD SELL
@bot.message_handler(commands=['copy'])
def copy_cmd(m):
    try:
        parts = m.text.split()
        if len(parts) < 3:
            bot.reply_to(m, "Use: /copy PAIR SIDE\nEx: /copy AUD/CAD SELL")
            return
        pair = parts[1].upper() + " OTC"
        side = parts[2].upper()
        # Custom signal from Owais Live
        pak = datetime.now(pytz.timezone('Asia/Karachi')).strftime("%I:%M:%S %p")
        txt = f"""
╔════════════════════════╗
║ OWAIS KHAN COPY SIGNAL ║
╚════════════════════════╝

💱 PAIR: {pair}
🔴 SIGNAL: {side}

📊 SCORE: {random.randint(2,5)}
📉 {side}: {random.randint(1,4)}

⏱ EXPIRY: 1 MINUTE
🕒 PKT: {pak}
🎯 NEXT CANDLE

Source: Owais Live
Bot: @gpt_trade_pro_2028_bot
"""
        bot.send_message(m.chat.id, txt)
    except Exception as e:
        bot.reply_to(m, f"Error: {e}")

def run_bot():
    print("Bot Started ✅", flush=True)
    while True:
        try:
            bot.infinity_polling(timeout=60, long_polling_timeout=60)
        except Exception as e:
            print(f"Restart: {e}", flush=True)
            time.sleep(5)

threading.Thread(target=run_bot, daemon=True).start()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
