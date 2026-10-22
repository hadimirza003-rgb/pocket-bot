# Forex Trading Bot - EUR/USD (World No.1 Pair)
# Created for Muhammad Aqeel
# pip install yfinance pandas pandas_ta

import yfinance as yf
import pandas as pd
import pandas_ta as ta

# CONFIG
PAIR = "EURUSD=X"  # Yahoo Finance Symbol for EUR/USD
TIMEFRAME = "1h"   # 1 hour chart - best for EUR/USD
EMA_FAST = 20
EMA_SLOW = 50
RSI_PERIOD = 14
STOP_LOSS_PIPS = 20
TAKE_PROFIT_PIPS = 40

print(f"Bot Started for {PAIR} - World's No.1 Pair")

# 1. DATA LO
data = yf.download(PAIR, period="60d", interval=TIMEFRAME)
data.dropna(inplace=True)

# 2. INDICATORS
data['EMA_FAST'] = ta.ema(data['Close'], length=EMA_FAST)
data['EMA_SLOW'] = ta.ema(data['Close'], length=EMA_SLOW)
data['RSI'] = ta.rsi(data['Close'], length=RSI_PERIOD)

# 3. SIGNALS
def get_signal(df):
    last = df.iloc[-1]
    prev = df.iloc[-2]
    
    # Buy Signal
    if (prev['EMA_FAST'] < prev['EMA_SLOW'] and 
        last['EMA_FAST'] > last['EMA_SLOW'] and 
        last['RSI'] < 70):
        return "BUY", last['Close']
    
    # Sell Signal
    if (prev['EMA_FAST'] > prev['EMA_SLOW'] and 
        last['EMA_FAST'] < last['EMA_SLOW'] and 
        last['RSI'] > 30):
        return "SELL", last['Close']
    
    return "HOLD", last['Close']

signal, price = get_signal(data)
print(f"Current Price: {price}")
print(f"Signal: {signal}")

# 4. CALCULATE SL/TP
if signal == "BUY":
    sl = price - (STOP_LOSS_PIPS * 0.0001)
    tp = price + (TAKE_PROFIT_PIPS * 0.0001)
    print(f">>> BUY EUR/USD at {price:.5f}")
    print(f"Stop Loss: {sl:.5f} | Take Profit: {tp:.5f}")

elif signal == "SELL":
    sl = price + (STOP_LOSS_PIPS * 0.0001)
    tp = price - (TAKE_PROFIT_PIPS * 0.0001)
    print(f">>> SELL EUR/USD at {price:.5f}")
    print(f"Stop Loss: {sl:.5f} | Take Profit: {tp:.5f}")

else:
    print("No Trade - Wait for Crossover")

# 5. BACKTEST (Last 60 days)
data['Signal'] = 0
data.loc[(data['EMA_FAST'] > data['EMA_SLOW']), 'Signal'] = 1
data.loc[(data['EMA_FAST'] < data['EMA_SLOW']), 'Signal'] = -1
data['Returns'] = data['Close'].pct_change() * data['Signal'].shift(1)
total_return = data['Returns'].sum() * 100
print(f"\nBacktest Return (60 days): {total_return:.2f}%")
