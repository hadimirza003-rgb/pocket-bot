import time,threading,yfinance as yf,pandas as pd,ta
from flask import Flask,jsonify
from datetime import datetime
app=Flask(__name__)
PAIRS={"EUR/USD":"EURUSD=X","GBP/USD":"GBPUSD=X","USD/JPY":"USDJPY=X","GBP/JPY":"GBPJPY=X","AUD/USD":"AUDUSD=X","EUR/JPY":"EURJPY=X","USD/CHF":"USDCHF=X","EUR/GBP":"EURGBP=X"}
last_signals={}
def get_data(s,i="1m",p="2d"):
 try:
  df=yf.download(s,period=p,interval=i,progress=False)
  if isinstance(df.columns,pd.MultiIndex):df.columns=df.columns.get_level_values(0)
  return df.dropna()
 except:return pd.DataFrame()
def filt(df1,df5):
 if len(df1)<100 or len(df5)<50:return None,"Data kam",0
 c=df1['Close'];h=df1['High'];l=df1['Low']
 r=ta.momentum.RSIIndicator(c,14).rsi();e9=ta.trend.EMAIndicator(c,9).ema_indicator();e21=ta.trend.EMAIndicator(c,21).ema_indicator();e50=ta.trend.EMAIndicator(c,50).ema_indicator();m=ta.trend.MACD(c);md=m.macd_diff();ml=m.macd();bb=ta.volatility.BollingerBands(c,20,2);bbh=bb.bollinger_hband();bbl=bb.bollinger_lband();atr=ta.volatility.AverageTrueRange(h,l,c,14).average_true_range();st=ta.momentum.StochasticOscillator(h,l,c).stoch()
 lc=c.iloc[-1];lr=r.iloc[-1];le9=e9.iloc[-1];le21=e21.iloc[-1];le50=e50.iloc[-1];lmd=md.iloc[-1];lml=ml.iloc[-1];lbh=bbh.iloc[-1];lbl=bbl.iloc[-1];la=atr.iloc[-1];ls=st.iloc[-1];pc=c.iloc[-2];pe9=e9.iloc[-2]
 c5=df5['Close'];e9_5=ta.trend.EMAIndicator(c5,9).ema_indicator();e21_5=ta.trend.EMAIndicator(c5,21).ema_indicator();up=e9_5.iloc[-1]>e21_5.iloc[-1];down=e9_5.iloc[-1]<e21_5.iloc[-1]
 if la<0.00035:return None,f"Slow {la:.5f}",int(lr)
 if abs(le9-le21)<0.00012:return None,"Sideways",int(lr)
 if abs(lc-le50)>la*5:return None,"Far EMA50",int(lr)
 cs=0;ps=0
 if lr<28:cs+=1
 if lr>72:ps+=1
 if le9>le21 and lc>le21:cs+=1
 if le9<le21 and lc<le21:ps+=1
 if lmd>0 and lml>0:cs+=1
 if lmd<0 and lml<0:ps+=1
 if lc<=lbl*1.001 and ls<20:cs+=1
 if lc>=lbh*0.999 and ls>80:ps+=1
 if pc<pe9 and lc>le9 and lc>le21:cs+=1
 if pc>pe9 and lc<le9 and lc<le21:ps+=1
 if up:cs+=1
 if down:ps+=1
 if cs>=5:return "STRONG CALL",f"{cs}/6 UP RSI{lr:.0f} STO{ls:.0f}",int(lr)
 if ps>=5:return "STRONG PUT",f"{ps}/6 DOWN RSI{lr:.0f} STO{ls:.0f}",int(lr)
 return None,f"WAIT R{lr:.0f} C:{cs} P:{ps} {'UP' if up else 'DOWN'}",int(lr)
def scan():
 global last_signals
 tmp={}
 for n,s in PAIRS.items():
  d1=get_data(s,"1m","2d");d5=get_data(s,"5m","5d")
  if d1.empty or d5.empty:tmp[n]={"signal":"No Data","reason":"-","rsi":0,"time":datetime.now().strftime('%H:%M:%S')};continue
  sig,rea,rsi=filt(d1,d5);tmp[n]={"signal":sig if sig else "WAIT","reason":rea,"rsi":rsi,"time":datetime.now().strftime('%H:%M:%S')}
 last_signals=tmp
def loop():
 while True:
  try:scan()
  except:pass
  time.sleep(120)
@app.route('/')
def home():
 h="<html><head><title>Super Strict</title><meta http-equiv='refresh' content='90'><style>body{font-family:sans-serif;background:#0a0a0a;color:#fff;padding:15px}.card{background:#1a1a1a;padding:12px;margin:8px;border-radius:10px;display:inline-block;width:200px}.call{border-left:6px solid #0f8}.put{border-left:6px solid #f34}.wait{border-left:4px solid #444}h1{color:#0f8;text-align:center}a{color:#0af}</style></head><body><h1>🔥 SUPER STRICT</h1><p style='text-align:center'>For m.pocketoption.com manual | 5/6 score | <a href='/signals'>JSON</a></p><div style='text-align:center'>"
 for p,d in last_signals.items():
  cl="call" if "CALL" in d['signal'] else "put" if "PUT" in d['signal'] else "wait";em="🟢💎" if "CALL" in d['signal'] else "🔴💎" if "PUT" in d['signal'] else "⏳";h+=f"<div class='card {cl}'><b>{p}</b><br><b>{em} {d['signal']}</b><br><small>{d['reason']}<br>{d['time']}</small></div>"
 h+="</div></body></html>";return h
@app.route('/signals')
def signals():return jsonify(last_signals)
threading.Thread(target=loop,daemon=True).start();threading.Thread(target=scan,daemon=True).start()
