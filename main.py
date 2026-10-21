def get_level(sym):
    try:
        # 5m aur 15m dono ka data
        df5 = yf.download(sym, period="1d", interval="5m", progress=False, auto_adjust=True)
        df15 = yf.download(sym, period="1d", interval="15m", progress=False, auto_adjust=True)
        if len(df5) < 50 or len(df15) < 50: return None
        
        for df in [df5, df15]:
            df['EMA20'] = df['Close'].ewm(span=20).mean()
            df['EMA50'] = df['Close'].ewm(span=50).mean()
            delta = df['Close'].diff()
            gain = (delta.where(delta>0,0)).rolling(14).mean()
            loss = (-delta.where(delta<0,0)).rolling(14).mean()
            df['RSI'] = 100 - (100/(1+gain/loss))
        
        p5 = float(df5['Close'].iloc[-1])
        rsi5 = float(df5['RSI'].iloc[-1])
        ema20_5 = float(df5['EMA20'].iloc[-1])
        ema50_5 = float(df5['EMA50'].iloc[-1])
        
        p15 = float(df15['Close'].iloc[-1])
        rsi15 = float(df15['RSI'].iloc[-1])

        low = float(df5['Low'][-20:].min())
        high = float(df5['High'][-20:].max())
        
        # --- PRO FILTER ---
        # Choppy market avoid
        if abs(ema20_5 - ema50_5) / p5 < 0.0008: # trend nahi hai
            return None

        # BUY CONDITION - Strong
        if p5 <= low*1.0015 and rsi5 < 35 and rsi15 < 45 and p5 > ema20_5 and ema20_5 > ema50_5:
            return f"BUY ✅ Level: {low:.5f} | RSI 5M:{rsi5:.0f} 15M:{rsi15:.0f} | TREND UP"

        # SELL CONDITION - Strong  
        if p5 >= high*0.9985 and rsi5 > 65 and rsi15 > 55 and p5 < ema20_5 and ema20_5 < ema50_5:
            return f"SELL ✅ Level: {high:.5f} | RSI 5M:{rsi5:.0f} 15M:{rsi15:.0f} | TREND DOWN"

        return None
    except Exception as e:
        print(f"Error {sym}: {e}")
        return None
        PAIRS = {
    "EUR/USD":"EURUSD=X", 
    "GBP/USD":"GBPUSD=X", 
    "USD/JPY":"JPY=X",
    "GOLD":"GC=F",
    "GBP/JPY":"GBPJPY=X",
    "EUR/JPY":"EURJPY=X"
}
