import os
import requests
from flask import Flask, request

app = Flask(__name__)

TOKEN = os.environ.get("TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

BUY_LEVEL = 120000   # عدل مستوى الشراء
SELL_LEVEL = 30000   # عدل مستوى البيع


# -----------------------------
# جلب سعر البيتكوين من Binance
# -----------------------------
def get_price():
    try:
        url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
        response = requests.get(url, timeout=5)
        data = response.json()

        if "price" in data:
            return float(data["price"])
        else:
            print("Binance Error:", data)
            return None

    except Exception as e:
        print("Error fetching price:", e)
        return None


# -----------------------------
# إرسال رسالة
# -----------------------------
def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": chat_id,
        "text": text
    })


# -----------------------------
# فحص الشروط
# -----------------------------
def check_conditions(chat_id):
    price = get_price()

    if price is None:
        send_message(chat_id, "⚠️ فشل جلب سعر البيتكوين")
        return

    if price >= BUY_LEVEL:
        send_message(chat_id, f"🔥 إشارة شراء BTC\nالسعر الحالي: {price}")

    elif price <= SELL_LEVEL:
        send_message(chat_id, f"🔻 إشارة بيع BTC\nالسعر الحالي: {price}")

    else:
        send_message(chat_id, f"📊 السعر الحالي: {price}\nلا توجد إشارة حالياً")


# -----------------------------
# Webhook
# -----------------------------
@app.route("/", methods=["POST", "GET"])
def webhook():

    if request.method == "POST":
        data = request.get_json()

        if data and "message" in data:
            chat_id = data["message"]["chat"]["id"]
            text = data["message"].get("text", "")

            if text == "/start":
                send_message(chat_id, "🔥 بوت بيتكوين شغال بنجاح")

            elif text == "فحص":
                check_conditions(chat_id)

        return "OK", 200

    return "Bot Running", 200


# -----------------------------
# تشغيل السيرفر
# -----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
