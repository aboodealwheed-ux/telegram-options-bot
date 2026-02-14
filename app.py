import os
import requests
from flask import Flask, request

app = Flask(__name__)

TOKEN = os.environ.get("TOKEN")
API_URL = f"https://api.telegram.org/bot{TOKEN}"

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()

    if "channel_post" in data:
        chat_id = data["channel_post"]["chat"]["id"]
        text = data["channel_post"].get("text", "")

        # رد تجريبي
        if text.lower() == "test":
            send_message(chat_id, "🔥 البوت شغال 100%")

    return "ok", 200


def send_message(chat_id, text):
    requests.post(
        f"{API_URL}/sendMessage",
        json={"chat_id": chat_id, "text": text},
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
