# Pocket Option Signal Scanner - by Aqeel
# pip install yfinance pandas ta

import time
import pandas as pd
import yfinance as yf
import ta
from datetime import datetime

PAIRS = ["EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X", "EURJPY=X", "GBPJPY=X"]
TIMEFRAME = "1m"
SCAN_INTERVAL = 60  # 60 second

def get_data(symbol):
    df = yf.download(symbol, period="1d", interval="1m", progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df.dropna()

def check_signal(df):
    if len(df) < 50:
        return None, ""
    close = df['Close']
    rsi = ta.momentum.RSIIndicator(close, 14).rsi().iloc[-1]
    ema_fast = ta.trend.EMAIndicator(close, 9).ema_indicator().iloc[-1]
    ema_slow = ta.trend.EMAIndicator(close, 21).ema_indicator().iloc[-1]
    macd = ta.trend.MACD(close).macd_diff().iloc[-1]
    price = close.iloc[-1]
    bb_high = ta.volatility.BollingerBands(close).bollinger_hband().iloc[-1]
    bb_low = ta.volatility.BollingerBands(close).bollinger_lband().iloc[-1]

    if rsi < 30 and ema_fast > ema_slow and macd > 0 and price <= bb_low:
        return "CALL 🟢", f"RSI {rsi:.1f} Oversold + EMA Up"
    elif rsi > 70 and ema_fast < ema_slow and macd < 0 and price >= bb_high:
        return "PUT 🔴", f"RSI {rsi:.1f} Overbought + EMA Down"
    elif rsi < 35 and ema_fast > ema_slow:
        return "CALL Weak 🟡", f"RSI {rsi:.1f}"
   
