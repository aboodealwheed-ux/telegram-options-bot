import requests
import time
import threading
import os
from flask import Flask

# =========================
# بياناتك
# =========================
TOKEN = "حط_توكنك_هنا"
CHAT_ID = "حط_ايدي_القروب_هنا"

# =========================
# دالة ارسال رسالة
# =========================
def send(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": msg
    }
    requests.post(url, data=data)

# =========================
# جلب سعر BTC من Binance
# =========================
def get_price():
    url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
    r = requests.get(url).json()
    return float(r["price"])

# =========================
# منطق الاختبار
# =========================
def trading_logic():
    send("🚀 تم تشغيل بوت اختبار BTC")

    while True:
        try:
            price = get_price()
            send(f"💰 السعر الحالي BTC: {price}")
            time.sleep(30)

        except Exception as e:
            print("Error:", e)
            time.sleep(30)

# =========================
# Flask لتشغيل Render
# =========================
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot Running BTC Test"

def start_thread():
    t = threading.Thread(target=trading_logic)
    t.daemon = True
    t.start()

start_thread()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
