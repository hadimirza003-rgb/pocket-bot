import os
import threading
import yfinance as yf
import pandas as pd
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = os.environ.get("BOT_TOKEN")
app = Flask(__name__)

@app.route('/')
def home():
    return "GPT Trade Pro 2026 - Live ✅"

# --- TRADING LOGIC ---
def get_signal(pair="BTC-USD"):
    try:
        # Pair fix: BTCUSD -> BTC-USD
        if "-" not in pair and "/" not in pair:
            if "USD" in pair.upper():
                pair = pair.upper().replace("USD", "-USD")
            else:
                pair = f"{pair.upper()}-USD"
        pair = pair.replace("/", "-").upper()
        
        data = yf.download(pair, period="1d", interval="5m", progress=False)
        if len(data) < 50:
            return f"❌ {pair} ka data nahi mila. Sahi pair likho jaise: BTC-USD, EURUSD=X, AAPL"
        
        close = data['Close']
        # RSI
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        rsi_val = float(rsi.iloc[-1])

        # EMA
        ema9 = close.ewm(span=9).mean().iloc[-1]
        ema21 = close.ewm(span=21).mean().iloc[-1]
        price = float(close.iloc[-1])

        # Signal
        if rsi_val < 30 and price > ema9:
            signal = "🟢 STRONG BUY"
        elif rsi_val > 70 and price < ema9:
            signal = "🔴 STRONG SELL"
        elif ema9 > ema21 and rsi_val > 50:
            signal = "🟢 BUY"
        elif ema9 < ema21 and rsi_val < 50:
            signal = "🔴 SELL"
        else:
            signal = "⚪ WAIT / SIDEWAYS"

        return (
            f"📊 *{pair} SIGNAL*\n\n"
            f"💰 Price: `{price:.2f}`\n"
            f"📈 EMA9: `{float(ema9):.2f}` | EMA21: `{float(ema21):.2f}`\n"
            f"📉 RSI(14): `{rsi_val:.2f}`\n\n"
            f"🎯 *SIGNAL: {signal}*\n\n"
            f"⏰ Timeframe: 5M\n"
            f"🤖 GPT Trade Pro 2026"
        )
    except Exception as e:
        return f"❌ Error: {str(e)}\nSahi likho: /signal BTC-USD"

# --- COMMANDS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚀 *GPT TRADE PRO 2026 BOT ONLINE!*\n\n"
        "✅ Bot Ready Hai Aqeel!\n\n"
        "📋 *Commands:*\n"
        "/signal BTC-USD - BTC ka signal\n"
        "/signal EURUSD=X - Forex\n"
        "/signal AAPL - Stocks\n"
        "/pairs - Popular pairs list\n"
        "/help - Madad\n\n"
        "Example: `/signal BTC-USD`",
        parse_mode='Markdown'
    )

async def pairs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔥 *POPULAR PAIRS:*\n\n"
        "*Crypto:*\nBTC-USD, ETH-USD, SOL-USD\n\n"
        "*Forex:*\nEURUSD=X, GBPUSD=X, USDJPY=X\n\n"
        "*Stocks:*\nAAPL, TSLA, GOLD -> GC=F\n\n"
        "Use: `/signal BTC-USD`",
        parse_mode='Markdown'
    )

async def signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Pair likho!\nExample: `/signal BTC-USD`", parse_mode='Markdown')
        return
    pair = context.args[0]
    await update.message.reply_text("⏳ Analyzing... 2 sec...")
    result = get_signal(pair)
    await update.message.reply_text(result, parse_mode='Markdown')

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)

def run_bot():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("pairs", pairs))
    application.add_handler(CommandHandler("signal", signal))
    application.add_handler(CommandHandler("help", help_cmd))
    print("Bot Polling Started ✅")
    application.run_polling()

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
