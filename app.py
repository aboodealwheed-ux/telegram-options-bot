import os
import requests
from flask import Flask, request

app = Flask(__name__)

TOKEN = os.environ.get("TOKEN")
TELEGRAM_API = f"https://api.telegram.org/bot{TOKEN}"

# ارسال رسالة
def send_message(chat_id, text):
    url = f"{TELEGRAM_API}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    requests.post(url, json=payload)

# الصفحة الرئيسية
@app.route("/")
def home():
    return "BTC Bot Running"

# استقبال التحديثات من تيليجرام
@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()

    if "channel_post" in data:
        message = data["channel_post"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "").lower()

        # ترحيب تلقائي
        if text == "/start":
            welcome = """
🔥 أهلاً بكم في بوت عاقل بس مرجوج

✈️ نرجو منكم ربط الأحزمة

⚠️ للتنبيه: هذا لا يعد توصية استثمارية
"""
            send_message(chat_id, welcome)

        # شرط ارسال عقد بيتكوين
        if text == "btc":

            contract = f"""
📊 BTC SIGNAL

🟢 BUY

💰 Entry: 52000
🎯 TP1: 52300
🎯 TP2: 52600

🚀 عقد جاهز للتنفيذ
⚠️ إدارة رأس المال مسؤوليتك
"""

            send_message(chat_id, contract)

    return "ok"

# تشغيل السيرفر
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
