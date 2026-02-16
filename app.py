import os
import time
import threading
import requests
from flask import Flask

app = Flask(__name__)

TOKEN = os.environ.get("TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

symbol = "%5EGSPC"  # SPX

in_position = None

# -------- ارسال رسالة --------
def send(msg):
    try:
        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            json={"chat_id": CHAT_ID, "text": msg}
        )
    except:
        pass

# -------- جلب بيانات 1 دقيقة --------
def get_data():
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1m&range=1d"
    r = requests.get(url, timeout=10)
    data = r.json()

    closes = data["chart"]["result"][0]["indicators"]["quote"][0]["close"]
    closes = [c for c in closes if c is not None]
    return closes

# -------- حساب EMA --------
def ema(values, period):
    k = 2 / (period + 1)
    ema_values = [values[0]]
    for price in values[1:]:
        ema_values.append(price * k + ema_values[-1] * (1 - k))
    return ema_values

# -------- منطق التداول --------
def trading_logic():
    global in_position

    send("🚀 تم تشغيل بوت US500")

    while True:
        try:
            closes = get_data()

            if len(closes) < 30:
                time.sleep(30)
                continue

            ema9 = ema(closes, 9)
            ema21 = ema(closes, 21)

            current_price = closes[-1]

            # تقاطع صاعد
            if ema9[-1] > ema21[-1] and in_position != "BUY":
                send(f"🔥 BUY US500\nالسعر: {current_price}")
                in_position = "BUY"

            # تقاطع هابط
            elif ema9[-1] < ema21[-1] and in_position != "SELL":
                send(f"🔻 SELL US500\nالسعر: {current_price}")
                in_position = "SELL"

            time.sleep(60)

        except Exception as e:
            print("Error:", e)
            time.sleep(30)

# -------- تشغيل --------
def start_thread():
    t = threading.Thread(target=trading_logic)
    t.daemon = True
    t.start()

@app.route("/")
def home():
    return "US500 Bot Running"

start_thread()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
