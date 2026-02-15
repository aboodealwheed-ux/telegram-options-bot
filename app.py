import os
import requests
import threading
import time
import yfinance as yf
import pandas as pd
import math
from flask import Flask

app = Flask(__name__)

TOKEN = os.environ.get("TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

SYMBOL = "BTC-USD"
TIMEFRAME = "5m"

in_trade = False
direction = None
entry_price = 0
mode = "CALM"

# ---------------- Telegram ----------------
def send(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": msg})

# ---------------- Indicators ----------------
def calculate_atr(data, period=14):
    high_low = data["High"] - data["Low"]
    high_close = abs(data["High"] - data["Close"].shift())
    low_close = abs(data["Low"] - data["Close"].shift())
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    return tr.rolling(period).mean().iloc[-1]

def calculate_angle(data):
    y2 = data["Close"].iloc[-1]
    y1 = data["Close"].iloc[-6]
    slope = (y2 - y1) / 5
    return abs(math.degrees(math.atan(slope)))

# ---------------- Market Mode Detection ----------------
def detect_mode(data):
    atr = calculate_atr(data)
    atr_avg = data["High"].sub(data["Low"]).rolling(20).mean().iloc[-1]

    volume = data["Volume"].iloc[-1]
    avg_volume = data["Volume"].rolling(20).mean().iloc[-1]

    candle_range = data["High"].iloc[-1] - data["Low"].iloc[-1]
    avg_range = data["High"].sub(data["Low"]).rolling(15).mean().iloc[-1]

    if (
        atr > atr_avg * 1.5 or
        volume > avg_volume * 2 or
        candle_range > avg_range * 1.8
    ):
        return "AGGRESSIVE"
    return "CALM"

# ---------------- Trading Logic ----------------
def trading_logic():
    global in_trade, direction, entry_price, mode

    while True:
        try:
            data = yf.download(SYMBOL, period="1d", interval=TIMEFRAME)

            if len(data) < 50:
                time.sleep(60)
                continue

            price = data["Close"].iloc[-1]
            swing_high = data["High"].tail(15).max()
            swing_low = data["Low"].tail(15).min()

            volume = data["Volume"].iloc[-1]
            avg_volume = data["Volume"].tail(10).mean()

            angle = calculate_angle(data)
            mode = detect_mode(data)

            if not in_trade:

                # ---------- CALM MODE ----------
                if mode == "CALM":

                    ema50 = data["Close"].ewm(span=50).mean().iloc[-1]

                    if price > ema50 and price > swing_high and angle >= 30:
                        direction = "CALL"
                        entry_price = price
                        in_trade = True
                        send(f"""🟢 BTC CALM CALL

🎯 Entry: {round(price,2)}
📐 Angle: {round(angle)}°
""")

                    elif price < ema50 and price < swing_low and angle >= 30:
                        direction = "PUT"
                        entry_price = price
                        in_trade = True
                        send(f"""🔴 BTC CALM PUT

🎯 Entry: {round(price,2)}
📐 Angle: {round(angle)}°
""")

                # ---------- AGGRESSIVE MODE ----------
                if mode == "AGGRESSIVE":

                    if (
                        price > swing_high and
                        volume > avg_volume * 2 and
                        angle >= 60
                    ):
                        direction = "CALL"
                        entry_price = price
                        in_trade = True
                        send(f"""🔥 BTC AGGRESSIVE CALL

🎯 Entry: {round(price,2)}
📐 Angle: {round(angle)}°
💥 Volume Explosion
""")

                    elif (
                        price < swing_low and
                        volume > avg_volume * 2 and
                        angle >= 60
                    ):
                        direction = "PUT"
                        entry_price = price
                        in_trade = True
                        send(f"""🔥 BTC AGGRESSIVE PUT

🎯 Entry: {round(price,2)}
📐 Angle: {round(angle)}°
💥 Volume Explosion
""")

            else:
                # -------- Trade Management --------
                if mode == "CALM":
                    target = 1.02
                else:
                    target = 1.04

                if direction == "CALL" and price >= entry_price * target:
                    send("🎯 BTC Target Hit")
                    in_trade = False

                if direction == "PUT" and price <= entry_price * (2 - target):
                    send("🎯 BTC Target Hit")
                    in_trade = False

            time.sleep(60)

        except Exception as e:
            print("Error:", e)
            time.sleep(60)

# ---------------- Server ----------------
@app.route("/")
def home():
    return "Bot Running BTC"

def start_thread():
    t = threading.Thread(target=trading_logic)
    t.daemon = True
    t.start()

start_thread()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
