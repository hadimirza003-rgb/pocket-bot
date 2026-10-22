from flask import Flask
import yfinance as yf
import pandas as pd
import os

app = Flask(__name__)

PAIRS = {
    "EUR/USD (No.1)": "EURUSD=X",
    "GBP/USD": "GBPUSD=X",
    "GOLD (XAU/USD)": "GC=F",
    "BTC/USD": "BTC-USD",
    "USD/JPY": "JPY=X"
}

def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).ewm(alpha=1/period, adjust=False).mean()
    loss = (-delta.where(delta < 0, 0)).ewm(alpha=1/period, adjust=False).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def get_signal(symbol):
    try:
        data = yf.download(symbol, period="20d", interval="1h", progress=False, auto_adjust=True)
        if data.empty or len(data) < 55:
            return "WAIT", 0, 0
        
        close = data['Close']
        if isinstance(close, pd.DataFrame):
            close = close.iloc[:, 0]
        
        ema20 = close.ewm(span=20, adjust=False).mean()
        ema50 = close.ewm(span=50, adjust=False).mean()
        rsi = calculate_rsi(close, 14)
        
        last_close = float(close.iloc[-1])
        last_ema20 = float(ema20.iloc[-1])
        prev_ema20 = float(ema20.iloc[-2])
        last_ema50 = float(ema50.iloc[-1])
        prev_ema50 = float(ema50.iloc[-2])
        last_rsi = float(rsi.iloc[-1])
        
        if prev_ema20 < prev_ema50 and last_ema20 > last_ema50 and last_rsi < 68:
            return "BUY", last_close, last_rsi
        elif prev_ema20 > prev_ema50 and last_ema20 < last_ema50 and last_rsi > 32:
            return "SELL", last_close, last_rsi
        else:
            return "HOLD", last_close, last_rsi
    except Exception as e:
        return "ERROR", 0, 0

@app.route('/')
def home():
    html = """
    <html><head><title>Pocket Bot - Live</title>
    <meta http-equiv='refresh' content='60'>
    <style>body{font-family:Arial;background:#0e0e10;color:white;padding:20px}
    table{width:100%;border-collapse:collapse;background:#1e1e22}
    th,td{padding:12px;border:1px solid #333;text-align:center}
    th{background:#2d2d30} .buy{color:#00ff88;font-weight:bold} .sell{color:#ff4444;font-weight:bold}
    </style></head><body>
    <h2>POCKET-BOT - 5 PAIRS LIVE</h2>
    <table><tr><th>Pair</th><th>Price</th><th>RSI</th><th>Signal</th></tr>
    """
    for name, symbol in PAIRS.items():
        signal, price, rsi = get_signal(symbol)
        css = "buy" if "BUY" in signal else "sell" if "SELL" in signal else ""
        html += f"<tr><td>{name}</td><td>{price:.5f}</td><td>{rsi:.1f}</td><td class='{css}'>{signal}</td></tr>"
    
    html += "</table><p>Auto refresh 60s | LIVE</p></body></html>"
    return html

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
