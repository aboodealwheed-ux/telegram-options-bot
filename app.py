import os
import requests
from flask import Flask, request

app = Flask(__name__)

TOKEN = os.environ.get("TOKEN")
TELEGRAM_URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"


def send_message(chat_id, text):
    requests.post(TELEGRAM_URL, json={
        "chat_id": chat_id,
        "text": text
    })


@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        # رد في الخاص
        if text == "/start":
            send_message(chat_id, "🔥 البوت شغال وجاهز!")

        # رد في القروب
        elif "فحص" in text:
            send_message(chat_id, "✅ تم الفحص — البوت يعمل في القروب!")

    return "OK"


@app.route("/", methods=["GET"])
def home():
    return "Bot Running"
