from flask import Flask, request
import requests
import os

app = Flask(__name__)

TOKEN = "8028407647:AAF_lwuVMq2l1oPo27MyDesjG27M5-vPhP8"
CHANNEL_ID = "-1003790525302"

@app.route('/')
def home():
    return "Bot Running"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    return "ok"

# دالة لإرسال صفقة
def send_signal(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": text
    }
    requests.post(url, json=payload)

if __name__ == "__main__":
    app.run()
