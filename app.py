import os
import time
import threading
import requests
from flask import Flask

app = Flask(__name__)

TOKEN = os.environ.get("TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

# ---------------- ارسال رسالة ----------------
def send(msg):
    try:
        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            json={"chat_id": CHAT_ID, "text": msg}
        )
    except:
        pass

# ---------------- حلقة اختبار ----------------
def trading_logic():
    send("🚀 تم تشغيل البوت بنجاح")

    while True:
        send("🟢 البوت يعمل حالياً...")
        time.sleep(30)

# ---------------- تشغيل الثريد ----------------
def start_thread():
    t = threading.Thread(target=trading_logic)
    t.daemon = True
    t.start()

@app.route("/")
def home():
    return "Bot Alive"

start_thread()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
