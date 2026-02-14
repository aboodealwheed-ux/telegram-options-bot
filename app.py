from flask import Flask, request
import requests
import os

app = Flask(__name__)

TOKEN = os.environ.get("TOKEN")

# للتأكد أن السيرفر شغال
@app.route("/", methods=["GET"])
def home():
    return "Bot Running"

# هذا هو Webhook الذي يستقبل رسائل تيليجرام
@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()

    if not data:
        return "no data"

    # إذا كانت رسالة عادية
    if "message" in data:
        message = data["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "")

        # رد بسيط للتجربة
        reply = f"وصلت الرسالة: {text}"

        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": reply
            }
        )

    return "ok"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
