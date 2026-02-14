from flask import Flask
import requests
import os

app = Flask(__name__)

TOKEN = os.environ.get("TOKEN")
CHANNEL_ID = os.environ.get("CHAT_ID")

@app.route('/')
def home():
    return "Bot Running"

def send_signal(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": text
    }
    requests.post(url, json=payload)

# رسالة تجريبية عند تشغيل السيرفر
@app.before_first_request
def startup_message():
    send_signal("🚀 البوت اشتغل بنجاح!")

if __name__ == "__main__":
    app.run()
