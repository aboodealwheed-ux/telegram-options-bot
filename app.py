import os
import requests
from flask import Flask, request

app = Flask(__name__)

TOKEN = os.environ.get("TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

BUY_LEVEL = 100000
SELL_LEVEL = 90000


def get_price():
    url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
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

    else:
        send_message(f"ℹ️ لا توجد إشارة حالياً\nالسعر الحالي: {price}")


@app.route("/", methods=["POST", "GET"])
def webhook():
    if request.method == "POST":
        data = request.get_json()

        if data and "message" in data:
            chat_id = data["message"]["chat"]["id"]
            text = data["message"].get("text", "")

            if text == "/start":
                send_message("🔥 بوت بيتكوين شغال بنجاح")

            if text == "فحص":
                check_conditions()

        return "OK", 200

    return "Bot Running", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
