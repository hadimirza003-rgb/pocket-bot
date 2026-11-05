# Advanced Pocket Option Signal Bot - Strong Signal Only
# pip install yfinance pandas ta

import yfinance as yf
import pandas as pd
import ta
import time
from datetime import datetime

PAIRS = ["EURUSD=X", "GBPUSD=X", "USDJPY=X", "GBPJPY=X", "AUDUSD=X", "EURJPY=X"]
INTERVAL = "1m"

def get_data(symbol):
    df = yf.download(symbol, period="2d", interval=INTERVAL, progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df.dropna()

def advanced_filter(df):
    if len(df) < 100:
        return None, "Data kam hai"

    close = df['Close']
    high = df['High']
    low = df['Low']
    
    # Indicators
    rsi = ta.momentum.RSIIndicator(close, 14).rsi()
    ema9 = ta.trend.EMAIndicator(close, 9).ema_indicator()
    ema21 = ta.trend.EMAIndicator(close, 21).ema_indicator()
    macd_diff = ta.trend.MACD(close).macd_diff()
    bb = ta.volatility.BollingerBands(close, 20, 2)
    bb_h = bb.bollinger_hband()
    bb_l = bb.bollinger_lband()
    atr = ta.volatility.AverageTrueRange(high, low, close, 14).average_true_range()

    # Last values
    last_close = close.iloc[-1]
    last_rsi = rsi.iloc[-1]
    last_ema9 = ema9.iloc[-1]
    last_ema21 = ema21.iloc[-1]
    last_macd = macd_diff.iloc[-1]
    last_bb_h = bb_h.iloc[-1]
    last_bb_l = bb_l.iloc[-1]
    last_atr = atr.iloc[-1]

    # Filter 1: Market choppy to nahi? (ATR check)
    if last_atr < 0.0003:  # bahut slow market
        return None, "Market Slow - No Trade Zone"

    # Filter 2: Sideways check
    if abs(last_ema9 - last_ema21) < 0.0001:
        return None
