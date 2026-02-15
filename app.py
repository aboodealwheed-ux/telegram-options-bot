import os
import requests
from flask import Flask

app = Flask(__name__)

TOKEN = os.environ.get("TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": CHAT_ID,
        "text": text
    })

@app.route("/")
def home():
    return "Bot Running"

# ترسل رسالة مباشرة عند تشغيل السيرفر
send_message("🔥 البوت اشتغل بنجاح")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
