import os
import requests
import threading
import time
from datetime import datetime
import yfinance as yf
from flask import Flask, request

TOKEN = os.environ.get("BOT_TOKEN")
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"
CHAT_ID = None

app = Flask(__name__)

# =========================
# ارسال رسالة
# =========================
def send_message(text, chat_id):
    url = f"{BASE_URL}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    requests.post(url, json=payload)

# =========================
# تحديد جلسة آسيا (5:30م - 12ص)
# =========================
def asia_session():
    now = datetime.now()
    hour = now.hour
    minute = now.minute

    start = 17.5   # 5:30 PM
    end = 24       # 12 AM

    current = hour + minute/60
    return start <= current <= end

# =========================
# تحليل بسيط (تقاطع متوسطين)
# =========================
def analyze(symbol):
    df = yf.download(symbol, period="1d", interval="5m")

    if len(df) < 30:
        return None

    df["EMA9"] = df["Close"].ewm(span=9).mean()
    df["EMA21"] = df["Close"].ewm(span=21).mean()

    last = df.iloc[-1]

    if last["EMA9"] > last["EMA21"]:
        direction = "شراء"
    else:
        direction = "بيع"

    price = round(last["Close"], 2)

    msg = f"""📊 تنبيه جلسة آسيا

الأصل: {symbol}
السعر: {price}
الاتجاه: {direction}
الفريم: 5 دقائق
"""

    return msg

# =========================
# البوت العامل بالخلفية
# =========================
def worker():
    global CHAT_ID
    while True:
        try:
            if CHAT_ID and asia_session():

                spx = analyze("^GSPC")
                gold = analyze("GC=F")

                if spx:
                    send_message(spx, CHAT_ID)

                if gold:
                    send_message(gold, CHAT_ID)

        except Exception as e:
            print("Error:", e)

        time.sleep(120)  # كل دقيقتين


# =========================
# الصفحة الرئيسية
# =========================
@app.route("/", methods=["GET"])
def home():
    return "Asia Bot Running"

# =========================
# استقبال التحديثات من تيليجرام
# =========================
@app.route("/", methods=["POST"])
def webhook():
    global CHAT_ID
    data = request.get_json(force=True)

    if "message" in data:
        CHAT_ID = data["message"]["chat"]["id"]
        text = data["message"].get("text")

        if text == "/start":
            send_message("🔥 تم تشغيل بوت جلسة آسيا", CHAT_ID)

    return "ok", 200


# =========================
# تشغيل السيرفر
# =========================
if __name__ == "__main__":
    t = threading.Thread(target=worker, daemon=True)
    t.start()
    app.run(host="0.0.0.0", port=10000)
