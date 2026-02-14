import os
import requests
from flask import Flask, request

app = Flask(__name__)

TOKEN = os.environ.get("TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

# ========== إعدادات بيتكوين ==========
SYMBOL = "BTCUSDT"
TIMEFRAME = "1h"
INTERVAL = 60

# مثال شروط بسيطة (نعدلها بعدين لزواياك)
BUY_LEVEL = 60000
SELL_LEVEL = 55000

# =====================================

def get_price():
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={SYMBOL}"
    data = requests.get(url).json()
    return float(data["price"])

def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": CHAT_ID,
        "text": text
    })

def check_conditions():
    price = get_price()

    if price >= BUY_LEVEL:
        send_message(f"🔥 إشارة شراء بيتكوين\nالسعر الحالي: {price}")

    elif price <= SELL_LEVEL:
        send_message(f"🔻 إشارة بيع بيتكوين\nالسعر الحالي: {price}")

@app.route("/", methods=["POST", "GET"])
def webhook():
    if request.method == "POST":
        data = request.get_json()
        if data and "message" in data:
            text = data["message"].get("text", "")

            if text == "/start":
                send_message("🔥 بوت بيتكوين شغال بنجاح")

            if text == "فحص":
                check_conditions()
                send_message("تم فحص الشروط")

        return "OK", 200

    return "Bot Running", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
