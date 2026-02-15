import os
import time
import threading
import requests
from flask import Flask

app = Flask(__name__)

TOKEN = os.environ.get("TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

# =====================
# ارسال رسالة
# =====================
def send(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": msg
    }
    requests.post(url, data=data)

# =====================
# جلب السعر من Binance
# =====================
def get_price():
    try:
        r = requests.get(
            "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT",
            timeout=5
        )
        return float(r.json()["price"])
    except:
        return None

# =====================
# مراقبة حركة 1%
# =====================
def trading_logic():

    base_price = None
    last_direction = None

    while True:
        try:
            price = get_price()

            if price is None:
                time.sleep(15)
                continue

            # أول سعر كبداية
            if base_price is None:
                base_price = price
                send(f"🤖 بدأ المراقبة\nالسعر الابتدائي: {price}")
                time.sleep(15)
                continue

            change_percent = ((price - base_price) / base_price) * 100

            # حركة صعود 1%
            if change_percent >= 1 and last_direction != "UP":
                send(f"🚀 صعود 1%\nالسعر: {price}\nالتغير: {change_percent:.2f}%")
                base_price = price
                last_direction = "UP"

            # حركة نزول 1%
            elif change_percent <= -1 and last_direction != "DOWN":
                send(f"🔻 نزول 1%\nالسعر: {price}\nالتغير: {change_percent:.2f}%")
                base_price = price
                last_direction = "DOWN"

            time.sleep(15)

        except Exception as e:
            print("Error:", e)
            time.sleep(15)

# =====================
# صفحة الموقع
# =====================
@app.route("/")
def home():
    return "Bot Running 1% Monitor"

# =====================
# تشغيل الثريد
# =====================
def start_thread():
    t = threading.Thread(target=trading_logic)
    t.daemon = True
    t.start()

start_thread()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
