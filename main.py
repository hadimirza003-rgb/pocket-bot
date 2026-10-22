from flask import Flask
import yfinance as yf
import pandas_ta as ta

app = Flask(__name__)

# TOP 5 PAIRS
PAIRS = {
    "EUR/USD": "EURUSD=X",
    "GBP/USD": "GBPUSD=X", 
    "GOLD": "GC=F",
    "BTC/USD": "BTC-USD",
    "USD/JPY": "JPY=X"
}

def get_signal_for_pair(symbol):
    try:
        data = yf.download(symbol, period="10d", interval="1h", progress=False)
        if len(data) < 60:
            return "WAIT", 0, 0
        
        data['EMA20'] = ta.ema(data['Close'], length=20)
        data['EMA50'] = ta.ema(data['Close'], length=50)
        data['RSI'] = ta.rsi(data['Close'], length=14)
        
        last = data.iloc[-1]
        prev = data.iloc[-2]
        
        # Strong Signal Logic
        if prev['EMA20'] < prev['EMA50'] and last['EMA20'] > last['EMA50'] and last['RSI'] < 65:
            return "🔥 BUY", float(last['Close']), float(last['RSI'])
        elif prev['EMA20'] > prev['EMA50'] and last['EMA20'] < last['EMA50'] and last['RSI'] > 35:
            return "🔻 SELL", float(last['Close']), float(last['RSI'])
        else:
            return "HOLD", float(last['Close']), float(last['RSI'])
    except:
        return "ERROR", 0, 0

@app.route('/')
def home():
    html = "<h1>🚀 POCKET-BOT - 5 PAIRS LIVE</h1><table border=1 style='width:100%; padding:10px'>"
    html += "<tr><th>Pair</th><th>Price</th><th>RSI</th><th>Signal</th></tr>"
    
    for name, symbol in PAIRS.items():
        signal, price, rsi = get_signal_for_pair(symbol)
        color = "green" if "BUY" in signal else "red" if "SELL" in signal else "gray"
        html += f"<tr><td><b>{name}</b></td><td>{price:.4f}</td><td>{rsi:.1f}</td><td style='color:{color}; font-weight:bold'>{signal}</td></tr>"
    
    html += "</table><p>Auto Refresh in 60s</p><meta http-equiv='refresh' content='60'>"
    return html

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
