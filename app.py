import os
import requests
from flask import Flask, request

app = Flask(__name__)

TOKEN = os.environ.get("TOKEN")

# مستويات تجريبية
BUY_LEVEL = 70000
SELL_LEVEL = 60000


# =========================
# جلب سعر البيتكوين
# =========================
def get_price():
    url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
    data = requests.get(url).json()
    return float(data["price"])


# =========================
# ارسال رسالة
# =========================
def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": chat_id,
        "text": text
    })


# =========================
# فحص الشروط
# =========================
def check_conditions(chat_id):
    price = get_price()

    if price >= BUY_LEVEL:
        send_message(chat_id, f"🔥 إشارة شراء بيتكوين\nالسعر الحالي: {price}")

    elif price <= SELL_LEVEL:
        send_message(chat_id, f"🔻 إشارة بيع بيتكوين\nالسعر الحالي: {price}")

    else:
        send_message(chat_id, f"⏳ لا توجد إشارة حالياً\nالسعر: {price}")


# =========================
# Webhook
# =========================
@app.route("/", methods=["POST", "GET"])
def webhook():

    if request.method == "POST":
        data = request.get_json()

        if data and "message" in data:

            text = data["message"].get("text", "")
            chat_id = data["message"]["chat"]["id"]

            if text == "/start":
                send_message(chat_id, "🔥 بوت بيتكوين شغال بنجاح")

            elif text == "فحص":
                check_conditions(chat_id)

        return "OK", 200

    return "Bot Running", 200


# =========================
# تشغيل السيرفر
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
