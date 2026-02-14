import os
import requests
from flask import Flask
import time
import threading

app = Flask(__name__)

TOKEN = os.environ.get("TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

BUY_LEVEL = 70000   # عدل الرقم
SELL_LEVEL = 60000  # عدل الرقم

def get_price():
    url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
    response = requests.get(url)
    data = response.json()
    return float(data["price"])

def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": CHAT_ID,
        "text": text
    })

def price_checker():
    while True:
        try:
            price = get_price()

            if price >= BUY_LEVEL:
                send_message(f"🔥 إشارة شراء بيتكوين\nالسعر الحالي: {price}")

            elif price <= SELL_LEVEL:
                send_message(f"🔻 إشارة بيع بيتكوين\nالسعر الحالي: {price}")

        except Exception as e:
            print("Error:", e)

        time.sleep(60)  # يفحص كل دقيقة

@app.route("/")
def home():
    return "Bot Running", 200

if __name__ == "__main__":
    thread = threading.Thread(target=price_checker)
    thread.start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
