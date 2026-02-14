import os
import requests
from flask import Flask, request

app = Flask(__name__)

TOKEN = os.environ.get("TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

@app.route("/")
def home():
    return "Bot Running"

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json()

    # إذا جت رسالة في الخاص
    if "message" in data:
        text = data["message"].get("text")

        # إذا كتب فحص
        if text == "فحص":
            requests.post(
                f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                json={
                    "chat_id": CHAT_ID,
                    "text": "🚀 إشعار صفقة تجريبي"
                }
            )

    return "ok"

if __name__ == "__main__":
    app.run()
