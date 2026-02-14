import os
import requests
from flask import Flask, request

app = Flask(__name__)

TOKEN = os.environ.get("TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

BUY_LEVEL = 70000
SELL_LEVEL = 60000

def get_price():
    url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
    data = requests.get(url).json()
    return float(data["price"])

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": chat_id,
        "text": text
    })

def check_conditions(chat_id):
    price = get_price()

    if price >= BUY_LEVEL:
        send_message(chat_id, f"🔥 إشارة شراء بيتكوين\nالسعر الحالي: {price}")
    elif price <= SELL_LEVEL:
        send_message(chat_id, f"🔻 إشارة بيع بيتكوين\nالسعر الحالي: {price}")
    else:
        send_message(chat_id, f"السعر الحالي {price} — لا توجد إشارة حالياً")

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()

    if not data:
        return "OK", 200

    # يدعم القروبات + القنوات + الخاص
    message = (
        data.get("message") or
        data.get("channel_post") or
        data.get("edited_message")
    )

    if message:
        chat_id = message["chat"]["id"]
        text = message.get("text", "")

        if text == "/start":
            send_message(chat_id, "🔥 بوت بيتكوين شغال")

        if text == "فحص":
            check_conditions(chat_id)

    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
