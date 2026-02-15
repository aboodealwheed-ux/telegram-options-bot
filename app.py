import os
import time
import threading
import requests
import pandas as pd
import yfinance as yf
from flask import Flask

app = Flask(__name__)

TOKEN = os.environ.get("TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

symbol = "BTC-USD"
interval = "5m"

in_trade = False

def send(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

def get_data():
    df = yf.download(symbol, interval=interval, period="2d")
    return df

def trading_logic():
    global in_trade
    while True:
        try:
            df = get_data()

            df["EMA9"] = df["Close"].ewm(span=9).mean()
            df["EMA21"] = df["Close"].ewm(span=21).mean()
            df["Body"] = abs(df["Close"] - df["Open"])
            df["AvgBody"] = df["Body"].rolling(10).mean()
            df["AvgVol"] = df["Volume"].rolling(20).mean()

            last = df.iloc[-1]

            trend_up = last["EMA9"] > last["EMA21"]
            trend_down = last["EMA9"] < last["EMA21"]

            volume_explosion = last["Volume"] >= last["AvgVol"] * 1.8
            strong_candle = last["Body"] > last["AvgBody"]

            day_high = df["High"].max()
            day_low = df["Low"].min()

            room_up = last["Close"] < day_high * 0.995
            room_down = last["Close"] > day_low * 1.005

            if not in_trade:
                if trend_up and volume_explosion and strong_candle and room_up:
                    in_trade = True
                    send(f"""🚀 BTC LONG هجومي
السعر: {last['Close']:.2f}
حجم انفجار مؤكد
EMA9 فوق EMA21 👿""")

                elif trend_down and volume_explosion and strong_candle and room_down:
                    in_trade = True
                    send(f"""💣 BTC SHORT هجومي
السعر: {last['Close']:.2f}
حجم انفجار مؤكد
EMA9 تحت EMA21 👿""")

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
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
