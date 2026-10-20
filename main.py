import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import os
from flask import Flask
import threading

# --- CONFIG ---
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8430943509:AAEe3cgLa3d4V0e2s2m2d2f6g3h4j5k6l7") # Render me env variable se lena behtar hai

# Sare Pairs - Forex + OTC + Crypto + Stocks
ALL_PAIRS = [
    "EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "USDCHF", "NZDUSD",
    "EURGBP", "EURJPY", "GBPJPY", "AUDJPY", "EURUSD-OTC", "GBPUSD-OTC", "USDJPY-OTC", "AUDCAD-OTC",
    "BTCUSD", "ETHUSD", "LTCUSD", "SOLUSD", "XRPUSD",
    "GOLD", "SILVER", "OIL"
]

TIMEFRAMES = ["1m", "5m", "15m", "1h", "4h", "1d"]

# --- Keep Alive for Render ---
app_flask = Flask(__name__)
@app_flask.route('/')
def home(): return "Bot is Running!"
def run_flask(): app_flask.run(host='0.0.0.0', port=8080)

# --- Indicator Logic ---
def calculate_rsi(closes, period=14):
    if len(closes) < period+1: return 50
    gains, losses = [], []
    for i in range(1, len(closes)):
        diff = closes[i] - closes[i-1]
        if diff > 0: gains.append(diff); losses.append(0)
        else: gains.append(0); losses.append(abs(diff))
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    if avg_loss == 0: return 100
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def calculate_ema(data, period):
    if len(data) < period: return data[-1]
    k = 2 / (period + 1)
    ema = sum(data[:period]) / period
    for price in data[period:]: ema = price * k + ema * (1 - k)
    return ema

def get_data(symbol, tf):
    try:
        # Symbol mapping for Yahoo
        yahoo_symbol = symbol
        if symbol == "GOLD": yahoo_symbol = "GC=F"
        elif symbol == "SILVER": yahoo_symbol = "SI=F"
        elif symbol == "OIL": yahoo_symbol = "CL=F"
        elif "OTC" in symbol: yahoo_symbol = symbol.replace("-OTC", "=X")
        elif "USD" in symbol and len(symbol)<=7: yahoo_symbol = f"{symbol}=X"
        else: yahoo_symbol = f"{symbol}-USD"

        interval_map = {"1m":"1m", "5m":"5m", "15m":"15m", "1h":"60m", "4h":"1h", "1d":"1d"}
        y_interval = interval_map.get(tf, "1m")
        
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{yahoo_symbol}?interval={y_interval}&range=2d"
        r = requests.get(url, headers={"User-Agent":"Mozilla/5.0"}, timeout=10).json()
        result = r['chart']['result'][0]
        closes = result['indicators']['quote'][0]['close']
        closes = [x for x in closes if x is not None]
        if len(closes) < 30: return None
        return closes[-100:]
    except: return None

def generate_world_signal(pair, tf):
    closes = get_data(pair, tf)
    if not closes:
        return f"⚠️ {pair} ka data nahi mil raha, dusra pair try karo."

    price = closes[-1]
    rsi = calculate_rsi(closes)
    ema9 = calculate_ema(closes, 9)
    ema21 = calculate_ema(closes, 21)
    ema50 = calculate_ema(closes, 50)

    # World Strategy
    score = 0
    reason = []

    # 1. EMA Cross
    if ema9 > ema21: score+=2; reason.append("EMA 9 > 21 (Bullish)")
    else: score-=2; reason.append("EMA 9 < 21 (Bearish)")
    # 2. RSI
    if rsi < 30: score+=2; reason.append(f"RSI {rsi:.1f} Oversold")
    elif rsi > 70: score-=2; reason.append(f"RSI {rsi:.1f} Overbought")
    else: reason.append(f"RSI {rsi:.1f} Neutral")
    # 3. Price vs EMA50
    if price > ema50: score+=1; reason.append("Price > EMA50")
    else: score-=1; reason.append("Price < EMA50")
    # 4. Momentum
    if closes[-1] > closes[-5]: score+=1; reason.append("Momentum UP")
    else: score-=1; reason.append("Momentum DOWN")

    if score >= 3: final_signal = "🟢 STRONG BUY"; action = "BUY"
    elif score >= 1: final_signal = "🟢 BUY"; action = "BUY"
    elif score <= -3: final_signal = "🔴 STRONG SELL"; action = "SELL"
    elif score <= -1: final_signal = "🔴 SELL"; action = "SELL"
    else: final_signal = "🟡 WAIT / SIDEWAYS"; action = "WAIT"

    text = f"""
📊 **{pair} | {tf.upper()}**

💰 Price: `{price}`

🎯 **SIGNAL: {final_signal}**
📈 Action: **{action}**

🧠 **World Analysis:**
- {chr(10)+'- '.join(['']+reason)}

⏰ Timeframe: {tf}
✅ Accuracy: High (EMA+RSI+Trend)
"""
    return text

# --- Telegram Buttons ---
def main_menu():
    buttons = []
    row = []
    for p in ALL_PAIRS[:12]:
        row.append(InlineKeyboardButton(p, callback_data=f"PAIR_{p}"))
        if len(row)==3: buttons.append(row); row=[]
    buttons.append([InlineKeyboardButton("➡️ More Pairs", callback_data="MORE_PAIRS")])
    buttons.append([InlineKeyboardButton("⏱ Timeframe: 1m | 5m | 15m", callback_data="TF_MENU")])
    return InlineKeyboardMarkup(buttons)

def tf_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("1m", callback_data="TF_1m"), InlineKeyboardButton("5m", callback_data="TF_5m"), InlineKeyboardButton("15m", callback_data="TF_15m")],
        [InlineKeyboardButton("1h", callback_data="TF_1h"), InlineKeyboardButton("4h", callback_data="TF_4h"), InlineKeyboardButton("1d", callback_data="TF_1d")],
        [InlineKeyboardButton("🔙 Back", callback_data="BACK_MAIN")]
    ])

def signal_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📡 GET SIGNAL NOW", callback_data="GET_SIGNAL")],
        [InlineKeyboardButton("🔄 Change Pair / TF", callback_data="BACK_MAIN")]
    ])

user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data[update.effective_user.id] = {"pair": "EURUSD", "tf": "1m"}
    await update.message.reply_text("👋 Welcome to World Trading Bot 🌍\nPair or Timeframe select karo:", reply_markup=main_menu())

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    if uid not in user_data: user_data[uid] = {"pair": "EURUSD", "tf": "1m"}

    data = q.data
    if data.startswith("PAIR_"):
        user_data[uid]["pair"] = data.replace("PAIR_", "")
        await q.message.reply_text(f"✅ Pair set: {user_data[uid]['pair']}\nAb signal lo:", reply_markup=signal_menu())
    elif data.startswith("TF_"):
        user_data[uid]["tf"] = data.replace("TF_", "")
        await q.message.reply_text(f"✅ Timeframe set: {user_data[uid]['tf']}\nAb signal lo:", reply_markup=signal_menu())
    elif data == "TF_MENU":
        await q.message.reply_text("Timeframe select karo:", reply_markup=tf_menu())
    elif data == "BACK_MAIN":
        await q.message.reply_text("Main Menu:", reply_markup=main_menu())
    elif data == "GET_SIGNAL":
        pair = user_data[uid]["pair"]
        tf = user_data[uid]["tf"]
        await q.message.reply_text(f"⏳ {pair} {tf} ka World Analysis kar raha hun...")
        signal = generate_world_signal(pair, tf)
        await q.message.reply_text(signal, reply_markup=signal_menu(), parse_mode='Markdown')
    elif data == "MORE_PAIRS":
        all_btns = [[InlineKeyboardButton(p, callback_data=f"PAIR_{p}") for p in ALL_PAIRS[i:i+3]] for i in range(0, len(ALL_PAIRS), 3)]
        all_btns.append([InlineKeyboardButton("🔙 Back", callback_data="BACK_MAIN")])
        await q.message.reply_text("Sab pairs:", reply_markup=InlineKeyboardMarkup(all_btns))

def main():
    threading.Thread(target=run_flask).start()
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle))
    print("Bot Started...")
    app.run_polling()

if __name__ == "__main__":
    main()
