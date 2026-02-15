import os
import time
import threading
import requests
import yfinance as yf
from flask import Flask

app = Flask(__name__)

TOKEN = os.environ.get("TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

# ==============================
# ارسال رسالة تيليجرام
# ==============================
def send(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": CHAT_ID,
        "text": msg
    })

# ==============================
# الاستراتيجية
# ==============================
in_trade = False
entry_price = 0
last_profit_alert = 0

def trading_logic():
    global in_trade, entry_price, last_profit_alert

    while True:
        try:
            data = yf.download("BTC-USD", period="1d", interval="5m")
            
            if len(data) < 30:
                time.sleep(60)
                continue

            close = data["Close"]

            ema9 = close.ewm(span=9).mean().iloc[-1]
            ema21 = close.ewm(span=21).mean().iloc[-1]
            current_price = close.iloc[-1]

            print("Price:", current_price, "EMA9:", ema9)

            # ==========================
            # دخول تجريبي للاختبار
            # ==========================
            if not in_trade and current_price > ema9:

                in_trade = True
                entry_price = current_price
                last_profit_alert = 0

                send(f"""
🚀 BTC TEST ENTRY

💰 Entry : {entry_price:.2f}
📊 EMA9 : {ema9:.2f}
📊 EMA21 : {ema21:.2f}
                """)

            # ==========================
            # تنبيه أرباح كل 100$
            # ==========================
            if in_trade:
                profit = current_price - entry_price

                if profit >= last_profit_alert + 100:
                    last_profit_alert += 100
                    send(f"💵 Profit Reached {int(last_profit_alert)}$")

            time.sleep(60)

        except Exception as e:
            print("Error:", e)
            time.sleep(60)

# ==============================
# تشغيل السيرفر
# ==============================
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
