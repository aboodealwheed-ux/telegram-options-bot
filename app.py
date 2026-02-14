import os
import requests
import time
import threading
from flask import Flask
import telebot

TOKEN = os.environ.get("TOKEN")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

CHAT_ID = None
last_signal = None

# ====== جلب بيانات BTC ======
def get_data():
    url = "https://api.binance.com/api/v3/klines"
    params = {
        "symbol": "BTCUSDT",
        "interval": "1m",
        "limit": 120
    }
    data = requests.get(url, params=params).json()
    closes = [float(candle[4]) for candle in data]
    highs = [float(candle[2]) for candle in data]
    lows = [float(candle[3]) for candle in data]
    return closes, highs, lows

# ====== حساب الزوايا ======
def calculate_angles(high, low):
    orbit = high - low
    return {
        "0": low,
        "45": low + orbit * 0.25,
        "90": low + orbit * 0.50,
        "135": low + orbit * 0.75,
        "180": high
    }

# ====== منطق الإشارة ======
def check_signal():
    global CHAT_ID, last_signal

    while True:
        try:
            if CHAT_ID is None:
                time.sleep(10)
                continue

            closes, highs, lows = get_data()
            current = closes[-1]
            high = max(highs)
            low = min(lows)

            angles = calculate_angles(high, low)

            # شراء
            if current > angles["135"] and last_signal != "BUY":
                message = f"""🚀 إشارة شراء BTC

السعر: {current}
كسر زاوية 135°
مدار نشط صاعد

🔥 دخول شراء"""
                bot.send_message(CHAT_ID, message)
                last_signal = "BUY"

            # بيع
            elif current < angles["45"] and last_signal != "SELL":
                message = f"""🔻 إشارة بيع BTC

السعر: {current}
كسر زاوية 45°
مدار نشط هابط

🔥 دخول بيع"""
                bot.send_message(CHAT_ID, message)
                last_signal = "SELL"

        except Exception as e:
            print("Error:", e)

        time.sleep(60)

# ====== ترحيب ======
@bot.message_handler(commands=['start'])
def start(message):
    global CHAT_ID
    CHAT_ID = message.chat.id

    bot.send_message(message.chat.id,
"""🔥 أهلاً بكم في بوت عاقل بس مرجوج

🧭 يعمل بنموذج الزوايا والمدارات
📊 يراقب BTCUSDT
⚠️ هذا لا يعد توصية استثمارية

تم تفعيل الرصد المداري...""")

# ====== تشغيل ======
def run_bot():
    bot.infinity_polling()

@app.route("/", methods=["GET"])
def home():
    return "BTC ORBIT BOT RUNNING"

if __name__ == "__main__":
    threading.Thread(target=check_signal).start()
    threading.Thread(target=run_bot).start()
    app.run(host="0.0.0.0", port=10000)
