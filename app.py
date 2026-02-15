import os
import requests
import time
import threading
from flask import Flask

app = Flask(__name__)

TOKEN = os.environ.get("TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

symbol = "%5EGSPC"  # SPX
in_trade = False

def send(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": CHAT_ID,
        "text": msg
    })

def get_spx_price():
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1m&range=1d"
    r = requests.get(url)
    data = r.json()
    return data["chart"]["result"][0]["meta"]["regularMarketPrice"]

def trading_logic():
    global in_trade

    send("🚀 تم تشغيل بوت SPX")

    last_price = None

    while True:
        try:
            price = get_spx_price()

            if last_price is not None:

                # كسر صاعد قوي
                if price > last_price + 5 and not in_trade:
                    send(f"🔥 SPX اختراق صاعد\nالسعر: {price}")
                    in_trade = True

                # كسر هابط قوي
                if price < last_price - 5 and in_trade:
                    send(f"❌ SPX انعكاس هابط\nالسعر: {price}")
                    in_trade = False

            last_price = price
            time.sleep(30)

        except Exception as e:
            print("Error:", e)
            time.sleep(10)

@app.route("/")
def home():
    return "SPX Bot Running"

def start_thread():
    t = threading.Thread(target=trading_logic)
    t.daemon = True
    t.start()

start_thread()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
