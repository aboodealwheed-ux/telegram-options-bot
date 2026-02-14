import os
import requests
import random
import threading
import time
from flask import Flask, request

# =============================
# الإعدادات
# =============================

TOKEN = os.environ.get("TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")  # حط آيدي القروب هنا في Environment

app = Flask(__name__)

TELEGRAM_URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

# =============================
# إرسال رسالة
# =============================

def send_message(text):
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    requests.post(TELEGRAM_URL, data=payload)

# =============================
# رسالة الترحيب
# =============================

def send_welcome():
    message = """
🔥 <b>أهلاً بكم في بوت عاقل بس مرجوج</b>

✈️ نرجو منكم ربط الأحزمة

⚠️ للتنبيه: هذا لا يعد توصية استثمارية
"""
    send_message(message)

# =============================
# اختيار عقد هجومي
# =============================

def generate_contract():
    strike = random.randint(200, 300)
    price = round(random.uniform(1.00, 2.99), 2)

    direction = random.choice(["CALL", "PUT"])

    message = f"""
🎯 <b>عقد مستهدف</b>

📌 النوع: {direction}
📌 السترايك: {strike}
💰 سعر الدخول: ${price}

━━━━━━━━━━━━━━━━━━
✨ القرار شخصي
القناة لا تتحمل أي مسؤولية
"""

    return message

# =============================
# مراقبة السوق (نسخة تجريبية 24 ساعة)
# =============================

def monitor_market():
    while True:
        time.sleep(60)  # يفحص كل دقيقة

        # شرط تجريبي (تقدر تغيره لاحقاً)
        condition = random.choice([True, False, False])

        if condition:
            contract = generate_contract()
            send_message(contract)

# =============================
# ويبهوك
# =============================

@app.route("/", methods=["POST"])
def webhook():
    return "OK", 200

# =============================
# تشغيل السيرفر
# =============================

if __name__ == "__main__":
    send_welcome()
    threading.Thread(target=monitor_market).start()
    app.run(host="0.0.0.0", port=10000)
