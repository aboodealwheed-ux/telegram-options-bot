import os
import requests
import time
import threading
import yfinance as yf
import numpy as np
from flask import Flask

app = Flask(__name__)

TOKEN = os.environ.get("TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

SYMBOL = "^GSPC"
last_signal = None

def send(msg):
    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json={"chat_id": CHAT_ID, "text": msg}
    )

def monitor():
    global last_signal
    
    while True:
        try:
            data = yf.download(tickers=SYMBOL, period="1d", interval="5m")

            if len(data) < 30:
                time.sleep(60)
                continue

            close = data["Close"]

            # ===== بداية الجلسة =====
            session_start_price = close.iloc[0]
            current_price = close.iloc[-1]
            bars = len(close)

            slope = (current_price - session_start_price) / bars
            angle = np.degrees(np.arctan(slope))

            ema9 = close.ewm(span=9).mean()
            ema21 = close.ewm(span=21).mean()

            prev9 = ema9.iloc[-2]
            prev21 = ema21.iloc[-2]
            curr9 = ema9.iloc[-1]
            curr21 = ema21.iloc[-1]

            strike = round(current_price / 5) * 5

            # ===== CALL =====
            if (
                prev9 < prev21 and 
                curr9 > curr21 and 
                angle >= 45 and
                last_signal != "CALL"
            ):
                last_signal = "CALL"
                send(f"""📈 SPX CALL

🎯 Strike : {strike}
💰 Entry : {current_price:.2f}
📐 Angle : {angle:.1f}°
""")

            # ===== PUT =====
            if (
                prev9 > prev21 and 
                curr9 < curr21 and 
                angle <= -45 and
                last_signal != "PUT"
            ):
                last_signal = "PUT"
                send(f"""📉 SPX PUT

🎯 Strike : {strike}
💰 Entry : {current_price:.2f}
📐 Angle : {angle:.1f}°
""")

            time.sleep(60)

        except Exception as e:
            print("Error:", e)
            time.sleep(60)

@app.route("/")
def home():
    return "Bot Running"

threading.Thread(target=monitor, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
