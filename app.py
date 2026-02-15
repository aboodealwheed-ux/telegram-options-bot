import os
import requests
import time
import threading
from flask import Flask

app = Flask(__name__)

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# ---------------- ارسال رسالة ----------------
def send(msg):
    try:
        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            json={"chat_id": CHAT_ID, "text": msg}
        )
    except:
        pass

# ---------------- جلب سعر SPX من Yahoo ----------------
def get_spx_price():
    try:
        url = "https://query1.finance.yahoo.com/v7/finance/quote?symbols=%5EGSPC"
        r = requests.get(url, timeout=10)
        data = r.json()
        return float(data["quoteResponse"]["result"][0]["regularMarketPrice"])
    except:
        send("❌ خطأ جلب سعر SPX")
        return None

# ---------------- منطق بسيط تجريبي ----------------
def bot_logic():
    send("🚀 تم تشغيل بوت SPX")

    last_signal = None

    while True:
        price = get_spx_price()

        if price:
            send(f"📊 سعر SPX الحالي: {price}")

            # مثال تجريبي
            if price > 7000 and last_signal != "SELL":
                send("🔴 إشارة بيع SPX")
                last_signal = "SELL"

            elif price < 6000 and last_signal != "BUY":
                send("🟢 إشارة شراء SPX")
                last_signal = "BUY"

        time.sleep(60)

# ---------------- تشغيل ----------------
def start_thread():
    t = threading.Thread(target=bot_logic)
    t.daemon = True
    t.start()

@app.route("/")
def home():
    return "Bot Running SPX"

start_thread()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
