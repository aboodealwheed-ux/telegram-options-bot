import os
import time
import threading
import requests
import yfinance as yf
import pandas as pd
from flask import Flask, request
from datetime import datetime
import pytz

TOKEN = os.environ.get("TOKEN")
CHAT_ID = None
LAST_DIRECTION = None
WELCOME_SENT = False

app = Flask(__name__)
KSA = pytz.timezone("Asia/Riyadh")

# =========================
# إرسال رسالة
# =========================
def send_message(text):
    if not CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": text})

# =========================
# تحليل الاتجاه
# =========================
def compute_direction():
    spx = yf.Ticker("^GSPC")
    data = spx.history(period="1d", interval="5m")

    if data.empty or len(data) < 30:
        return None

    data["EMA9"] = data["Close"].ewm(span=9).mean()
    data["EMA21"] = data["Close"].ewm(span=21).mean()

    last = data.iloc[-1]
    price = round(last["Close"], 2)

    ema_diff = abs(last["EMA9"] - last["EMA21"])

    direction = "CALL" if last["EMA9"] > last["EMA21"] else "PUT"

    if ema_diff > 3:
        strength = "🔥 قوي"
    elif ema_diff > 1:
        strength = "🔸 متوسط"
    else:
        strength = "🔹 ضعيف"

    return direction, price, strength

# =========================
# البحث عن عقد بين 2 و 3 دولار
# =========================
def find_contract(price, direction):

    base_strike = round(price / 5) * 5
    step = 5

    # نبحث 10 محاولات يمين ويسار
    for i in range(10):

        if direction == "CALL":
            strike = base_strike - (i * step)
        else:
            strike = base_strike + (i * step)

        # تقدير تقريبي لسعر العقد
        entry = round(price * 0.04 - (i * 0.15), 2)

        if 2.00 <= entry <= 3.00:
            return strike, entry

    return None, None

# =========================
# وقف ذكي
# =========================
def calculate_stop(entry):

    if entry < 3:
        return round(entry * 0.65, 2)
    elif entry < 6:
        return round(entry * 0.60, 2)
    else:
        return round(entry * 0.55, 2)

# =========================
# Worker
# =========================
def worker():
    global LAST_DIRECTION, WELCOME_SENT

    while True:
        try:
            now = datetime.now(KSA)
            hour = now.hour
            minute = now.minute

            # رسالة ترحيب 5:20 مساء
            if hour == 17 and minute == 20 and not WELCOME_SENT:
                send_message(
                    "━━━━━━━━━━━━━━━━━━\n"
                    "🤖 بوت عاقل بس مرجوج\n"
                    "━━━━━━━━━━━━━━━━━━\n\n"
                    "📊 سيتم تشغيل النظام بعد قليل\n"
                    "✈️ نرجو ربط الأحزمة\n\n"
                    "⚠️ هذا لا يعد توصية استثمارية"
                )
                WELCOME_SENT = True

            if hour == 1:
                WELCOME_SENT = False

            if CHAT_ID:
                result = compute_direction()
                if result:
                    direction, price, strength = result

                    strike, entry = find_contract(price, direction)

                    if not strike:
                        time.sleep(60)
                        continue

                    if direction != LAST_DIRECTION:
                        LAST_DIRECTION = direction

                        tp1 = round(entry * 1.3, 2)
                        tp2 = round(entry * 1.6, 2)
                        tp3 = round(entry * 2.0, 2)

                        stop = calculate_stop(entry)

                        now_time = now.strftime("%I:%M %p")

                        msg = (
                            "━━━━━━━━━━━━━━━━━━\n"
                            "🎯 عقد مستهدف – SPX\n\n"
                            f"📊 الاتجاه: {direction}\n"
                            f"💪 قوة الإشارة: {strength}\n"
                            f"🎯 Strike: {strike}\n\n"
                            f"💰 سعر الدخول: {entry}$\n\n"
                            f"🎯 هدف1: {tp1}$\n"
                            f"🎯 هدف2: {tp2}$\n"
                            f"🎯 هدف3: {tp3}$\n\n"
                            f"🛑 وقف: {stop}$\n\n"
                            f"⏰ الوقت: {now_time}\n\n"
                            "⚠️ هذا لا يعد توصية استثمارية\n"
                            "━━━━━━━━━━━━━━━━━━"
                        )

                        send_message(msg)

        except Exception as e:
            print("Error:", e)

        time.sleep(60)

# =========================
# Routes
# =========================
@app.route("/", methods=["GET"])
def home():
    return "SPX PRO Bot Running"

@app.route("/", methods=["POST"])
def webhook():
    global CHAT_ID
    data = request.get_json(force=True)

    if "message" in data:
        CHAT_ID = data["message"]["chat"]["id"]
        text = data["message"].get("text")

        if text == "/start":
            send_message(
                "🔥 تم تشغيل بوت SPX الاحترافي\n"
                "سيتم إرسال إشارات عند تغير الاتجاه فقط"
            )

    return "ok", 200

# =========================
# تشغيل
# =========================
if __name__ == "__main__":
    t = threading.Thread(target=worker, daemon=True)
    t.start()
    app.run(host="0.0.0.0", port=10000)
