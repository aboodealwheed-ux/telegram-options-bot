import os
import time
import threading
import requests
import pandas as pd
import yfinance as yf
from flask import Flask, request

app = Flask(__name__)

TOKEN = os.environ.get("TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

symbol = "BTC-USD"
interval = "5m"

# -------- Telegram --------
def send(text):
    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": text}
    )

# -------- Data --------
def get_data():
    df = yf.download(symbol, interval=interval, period="2d")
    return df

# -------- Trading Logic (More Signals) --------
def trading_logic():
    while True:
        try:
            df = get_data()

            if len(df) < 30:
                time.sleep(60)
                continue

            df["EMA9"] = df["Close"].ewm(span=9).mean()
            df["EMA21"] = df["Close"].ewm(span=21).mean()
            df["Body"] = abs(df["Close"] - df["Open"])
            df["AvgBody"] = df["Body"].rolling(10).mean()
            df["AvgVol"] = df["Volume"].rolling(20).mean()

            last = df.iloc[-1]

            trend_up = last["EMA9"] > last["EMA21"]
            trend_down = last["EMA9"] < last["EMA21"]

            volume_explosion = last["Volume"] >= last["AvgVol"] * 1.2
            strong_candle = last["Body"] > last["AvgBody"] * 0.8

            if trend_up and volume_explosion and strong_candle:
                send(f"""🚀 BTC LONG هجومي
السعر: {last['Close']:.2f}
حجم مرتفع
EMA9 فوق EMA21 👿""")

            elif trend_down and volume_explosion and strong_candle:
                send(f"""💣 BTC SHORT هجومي
السعر: {last['Close']:.2f}
حجم مرتفع
EMA9 تحت EMA21 👿""")

            time.sleep(60)

        except Exception as e:
            print("Error:", e)
            time.sleep(60)

# -------- Webhook (يرد في الخاص فقط) --------
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json()

    if "message" in data:
        chat = data["message"]["chat"]
        chat_id = chat["id"]
        chat_type = chat["type"]

        if chat_type == "private":
            requests.post(
                f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                data={"chat_id": chat_id, "text": "البوت يعمل ويرسل إشعارات في القروب 👿🔥"}
            )

    return "ok"

@app.route("/")
def home():
    return "Bot Running BTC Aggressive"

def start_thread():
    t = threading.Thread(target=trading_logic)
    t.daemon = True
    t.start()

start_thread()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
