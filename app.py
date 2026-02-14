import os
import requests
from flask import Flask, request

TOKEN = os.environ.get("TOKEN")
TELEGRAM_API = f"https://api.telegram.org/bot{TOKEN}"

app = Flask(__name__)

def send_message(chat_id, text):
    url = f"{TELEGRAM_API}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    requests.post(url, json=payload)

@app.route("/", methods=["GET"])
def home():
    return "SPX PRO Bot Running"

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if text == "/start":
            send_message(chat_id,
                         "🔥 أهلاً بكم في بوت عاقل بس مرجوج\n\n"
                         "نرجو منكم ربط الأحزمة ✈️\n\n"
                         "⚠️ للتنبيه: هذا لا يعد توصية استثمارية")

    return "ok"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
