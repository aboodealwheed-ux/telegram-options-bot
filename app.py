import os
import threading
import time
import requests
import yfinance as yf
from flask import Flask

app = Flask(__name__)

TOKEN = os.environ.get("TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

# ====== إعدادات ======
SYMBOL = "^GSPC"      # SPX
INTERVAL = "5m"       # فريم 5 دقائق
MA_FAST = 9
MA_SLOW = 21

in_trade = False
entry_price = 0
last_profit_alert = 0


def send(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": CHAT_ID,
        "text": message
    })


def trading_logic():
    global in_trade, entry_price, last_profit_alert

    while True:
        try:
            data = yf.download(tickers=SYMBOL, period="1d", interval=INTERVAL)

            if len(data) < MA_SLOW:
                time.sleep(60)
                continue

            data["MA_FAST"] = data["Close"].rolling(MA_FAST).mean()
            data["MA_SLOW"] = data["Close"].rolling(MA_SLOW).mean()

            last = data.iloc[-1]
            prev = data.iloc[-2]

            # تقاطع صاعد دخول
            if not in_trade and prev["MA_FAST"] < prev["MA_SLOW"] and last["MA_FAST"] > last["MA_SLOW"]:
                entry_price = float(last["Close"])
                in_trade = True
                last_profit_alert = 0

                send(
                    f"""📈 دخول CALL SPX

سعر الدخول: {entry_price:.2f}
المتوسطات: 9 / 21
"""
                )

            # إدارة الربح
            if in_trade:
                current_price = float(last["Close"])
                profit = current_price - entry_price

                # كل 10 نقاط ربح ينبه
                if profit >= last_profit_alert + 10:
                    last_profit_alert += 10
                    send(f"💰 ربح +{int(last_profit_alert)} نقطة")

                # تحقق 2X
                if current_price >= entry_price * 1.02:
                    send(f"🎯 تحقق هدف 2X عند {current_price:.2f}")
                    in_trade = False

            time.sleep(60)

        except Exception as e:
            print("Error:", e)
            time.sleep(60)


@app.route("/")
def home():
    return "Bot Running"


def start_thread():
    t = threading.Thread(target=trading_logic)
    t.daemon = True
    t.start()


start_thread()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
