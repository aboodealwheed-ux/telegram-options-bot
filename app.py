import os
import requests
from flask import Flask, request

app = Flask(__name__)

TOKEN = os.environ.get("TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": text
    }
    requests.post(url, data=data)

@app.route("/", methods=["GET"])
def home():
    return "Bot Running"

@app.route("/", methods=["POST"])
def webhook():
    data = request.json

    if "message" in data:
        text = data["message"].get("text", "")

        if text == "/start":
            send_message("البوت شغال ✅")

    return "ok"
