import os, time, threading, yfinance as yf, pandas as pd, ta
from flask import Flask, jsonify
from datetime import datetime

TOKEN = os.environ.get("TELEGRAM_TOKEN", "").strip()
app = Flask(__name__)
PAIRS = {"EUR/USD":"EURUSD=X","GBP/USD":"GBPUSD=X","USD/JPY":"USDJPY=X","GBP/JPY":"GBPJPY=X","AUD/USD":"AUDUSD=X","EUR/JPY":"EURJPY=X","USD/CHF":"USDCHF=X","EUR/GBP":"EURGBP=X"}
last_signals = {}

def get_data(s,i="1m",p="2d"):
    try:
        df=yf.download(s,period=p,interval=i,progress=False,auto_adjust=False)
        if isinstance(df.columns,pd.MultiIndex):df.columns=df.columns.get_level_values(0)
        return df.dropna()
    except:return pd.DataFrame()

def filt(df1,df5):
    if len(df1)<100 or len(df5)<50:return None,"Wait",0
    c=df1['Close'];r=ta.momentum.RSIIndicator(c,14).rsi();e9=ta.trend.EMAIndicator(c,9).ema_indicator();e21=ta.trend.EMAIndicator(c,21).ema_indicator();m=ta.trend.MACD(c);md=m.macd_diff();bb=ta.volatility.BollingerBands(c,20,2);bbh=bb.bollinger_hband();bbl=bb.bollinger_lband();atr=ta.volatility.AverageTrueRange(df1['High'],df1['Low'],c,14).average_true_range();st=ta.momentum.StochasticOscillator(df1['High'],df1['Low'],c).stoch()
    lc=c.iloc[-1];lr=r.iloc[-1];le9=e9.iloc[-1];le21=e21.iloc[-1];la=atr.iloc[-1];ls=st.iloc[-1];pc=c.iloc[-2];pe9=e9.iloc[-2];c5=df5['Close'];e9_5=ta.trend.EMAIndicator(c5,9).ema_indicator();e21_5=ta.trend.EMAIndicator(c5,21).ema_indicator();up=e9_5.iloc[-1]>e21_5.iloc[-1];down=e9_5.iloc[-1]<e21_5.iloc[-1]
    if la<0.00015:return None,f"Slow {la:.5f}",int(lr)
    if abs(le9-le21)<0.00008:return None,"Sideways",int(lr)
    cs=0;ps=0
    if lr<32:cs+=1
    if lr>68:ps+=1
    if le9>le21 and lc>le21:cs+=1
    if le9<le21 and lc<le21:ps+=1
    if md.iloc[-1]>0:cs+=1
    if md.iloc[-1]<0:ps+=1
    if lc<=bbl.iloc[-1]*1.002 and ls<30:cs+=1
    if lc>=bbh.iloc[-1]*0.998 and ls>70:ps+=1
    if pc<pe9 and lc>le9:cs+=1
    if pc>pe9 and lc<le9:ps+=1
    if up:cs+=1
    if down:ps+=1
    if cs>=4:return "STRONG CALL",f"{cs}/6 UP RSI{lr:.0f}",int(lr)
    if ps>=4:return "STRONG PUT",f"{ps}/6 DOWN RSI{lr:.0f}",int(lr)
    return None,f"WAIT R{lr:.0f} C:{cs} P:{ps}",int(lr)

def scan():
    global last_signals
    tmp={}
    for n,s in PAIRS.items():
        d1=get_data(s,"1m","2d");d5=get_data(s,"5m","5d")
        if d1.empty or d5.empty:tmp[n]={"signal":"No Data","reason":"-","rsi":0,"time":datetime.now().strftime('%H:%M:%S')};continue
        sig,reason,rsi_val=filt(d1,d5)
        tmp[n]={"signal":sig if sig else "WAIT","reason":reason,"rsi":rsi_val,"time":datetime.now().strftime('%H:%M:%S')}
    last_signals=tmp
    return tmp

bot=None
if TOKEN:
    import telebot
    bot=telebot.TeleBot(TOKEN, threaded=False)
    @bot.message_handler(commands=['start','help','signal','pairs'])
    def cmd(m):
        data=scan()
        strong={k:v for k,v in data.items() if "STRONG" in v['signal']}
        if strong:
            msg="🚨 *STRONG SIGNALS* 🚨\n\n"
            for k,v in strong.items():msg+=f"💎 {k}: {v['signal']}\n   {v['reason']}\n\n"
        else:
            msg="⏳ *No STRONG now* - Market slow\n\n"
            for k,v in data.items():msg+=f"{k}: {v['signal']} - {v['reason']}\n"
        bot.reply_to(m,msg,parse_mode="Markdown")
    @bot.message_handler(func=lambda m: "SIGNAL" in m.text.upper() if m.text else False)
    def sig_lo(m):cmd(m)
    @bot.message_handler(func=lambda m: True)
    def any_m(m):cmd(m)
    def polling():
        while True:
            try:bot.infinity_polling(timeout=60,long_polling_timeout=60,skip_pending=True)
            except:time.sleep(10)
    threading.Thread(target=polling,daemon=True).start()

def loop():
    while True:
        try:scan()
        except:pass
        time.sleep(120)

@app.route('/')
def home():
    h=f"<h1>🔥 SUPER STRICT LIVE</h1><p>Last: {datetime.now().strftime('%H:%M:%S')}</p><div>"
    for p,d in last_signals.items():h+=f"<div><b>{p}</b>: {d['signal']} - {d['reason']}</div>"
    return h
@app.route('/signals')
def signals_api():return jsonify(last_signals)
if not hasattr(app,'_threads_started'):
    threading.Thread(target=loop,daemon=True).start()
    threading.Thread(target=scan,daemon=True).start()
    app._threads_started=True
if __name__=='__main__':
    app.run(host="0.0.0.0",port=int(os.environ.get("PORT",5000)))
