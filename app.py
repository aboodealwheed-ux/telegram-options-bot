import os
import requests
import time
import threading
import yfinance as yf
from flask import Flask

app = Flask(__name__)

TOKEN = os.environ.get("TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

# إعدادات المحاكاة
DELTA = 0.45
TIME_VALUE = 2.50

in_trade = False
entry_price = 0
strike_price = 0
entry_spx = 0
last_profit_alert = 0

def send(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": msg})

def get_spx():
    data = yf.Ticker("^GSPC")
    df = data.history(period="1d", interval="1m")
    return df

def calculate_ema(series, period):
    return series.ewm(span=period, adjust=False).mean()

def trading_logic():
    global in_trade, entry_price, strike_price, entry_spx, last_profit_alert
    
    while True:
        try:
            df = get_spx()
            if len(df) < 30:
                time.sleep(60)
                continue

            close = df["Close"]
            high = df["High"].max()
            low = df["Low"].min()

            ema9 = calculate_ema(close, 9).iloc[-1]
            ema21 = calculate_ema(close, 21).iloc[-1]
            current_price = close.iloc[-1]

            # دخول شراء
            if not in_trade and ema9 > ema21 and current_price > high:
                in_trade = True
                entry_spx = current_price
                strike_price = round(current_price / 5) * 5
                entry_price = TIME_VALUE
                last_profit_alert = 0

                send(f"""
━━━━━━━━━━━━━━━━━━
📈 SPX CALL

🎯 Strike : {strike_price}
💰 Entry : {entry_price:.2f}

━━━━━━━━━━━━━━━━━━
""")

            # متابعة الربح
            if in_trade:
                move = current_price - entry_spx
                option_price = entry_price + (move * DELTA)
                profit = (option_price - entry_price) * 100

                if profit >= last_profit_alert + 100:
                    last_profit_alert += 100
                    send(f"""
💰 +{int(last_profit_alert)}$
السعر : {option_price:.2f}
""")

                if option_price >= entry_price * 2:
                    send(f"""
🚀 2X تحققت
السعر : {option_price:.2f}
""")
                    in_trade = False

            time.sleep(60)

        except Exception as e:
            print("Error:", e)
            time.sleep(60)

@app.route("/")
def home():
    return "Bot Running"

def start_thread():
    t = threading.Thread(target=trading_logic)
    t.daemon = True
    t.start()

start_thread()

if __name__ == "__main__":
    app.run()
