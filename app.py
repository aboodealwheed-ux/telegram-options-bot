import os
import time
import threading
import requests
from flask import Flask

app = Flask(__name__)

TOKEN = os.environ.get("TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

symbol = "ES=F"  # عقود S&P500 الآجلة

def send(msg):
    try:
        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            json={"chat_id": CHAT_ID, "text": msg}
        )
    except:
        pass

def get_price():
    try:
        url = f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={symbol}"
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        r = requests.get(url, headers=headers, timeout=10)
        data = r.json()
        return data["quoteResponse"]["result"][0]["regularMarketPrice"]
    except Exception as e:
        return None

def bot_logic():
    send("🚀 تم تشغيل بوت سعر US500 (ES)")

    while True:
        price = get_price()

        if price:
            send(f"📊 سعر US500 الحالي: {price}")
        else:
            send("❌ فشل جلب السعر")

        time.sleep(60)

def start_thread():
    t = threading.Thread(target=bot_logic)
    t.daemon = True
    t.start()

@app.route("/")
def home():
    return "US500 Price Bot Running"

start_thread()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
