import os
import requests
import pandas as pd
import time
import threading
from flask import Flask

app = Flask(__name__)

TOKEN = os.environ.get("TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

last_signal = None

def get_klines():
    url = "https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=5m&limit=100"
    data = requests.get(url).json()
    closes = [float(candle[4]) for candle in data]
    return closes

def calculate_ema(prices, period):
    return pd.Series(prices).ewm(span=period, adjust=False).mean()

def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": CHAT_ID,
        "text": text
    })

def check_signal():
    global last_signal

    prices = get_klines()
    ema20 = calculate_ema(prices, 20)
    ema50 = calculate_ema(prices, 50)

    if ema20.iloc[-1] > ema50.iloc[-1] and last_signal != "buy":
        send_message(f"🔥 تقاطع صعودي BTC\nالسعر: {prices[-1]}")
        last_signal = "buy"

    elif ema20.iloc[-1] < ema50.iloc[-1] and last_signal != "sell":
        send_message(f"🔻 تقاطع هبوطي BTC\nالسعر: {prices[-1]}")
        last_signal = "sell"

def auto_checker():
    while True:
        try:
            check_signal()
        except Exception as e:
            print("Error:", e)

        time.sleep(300)  # كل 5 دقائق

@app.route("/")
def home():
    return "Bot Running", 200

if __name__ == "__main__":
    thread = threading.Thread(target=auto_checker)
    thread.start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
