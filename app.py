import requests
import time
import threading
import os
import math
from flask import Flask

TOKEN = "8028407647:AAF_lwuVMq2l1oPo27MyDesjG27M5-vPhP8"
CHAT_ID = "-1003790525302"

# =========================
# ارسال رسالة
# =========================
def send(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": msg}
    requests.post(url, data=data)

# =========================
# جلب بيانات SPX
# =========================
def get_spx_data():
    url = "https://query1.finance.yahoo.com/v8/finance/chart/^GSPC?range=1d&interval=5m"
    r = requests.get(url).json()
    result = r["chart"]["result"][0]
    closes = result["indicators"]["quote"][0]["close"]
    volumes = result["indicators"]["quote"][0]["volume"]

    data = []
    for i in range(len(closes)):
        if closes[i] is not None:
            data.append({
                "close": closes[i],
                "volume": volumes[i]
            })
    return data

# =========================
# حساب EMA
# =========================
def ema(values, period):
    k = 2 / (period + 1)
    ema_vals = [values[0]]
    for price in values[1:]:
        ema_vals.append(price * k + ema_vals[-1] * (1 - k))
    return ema_vals

# =========================
# اختيار Strike ذكي
# =========================
def nearest_strike(price, step=5):
    return round(price / step) * step

def choose_strike(price, strength, direction):
    base = nearest_strike(price)

    if strength < 1:
        offset = 0
    elif strength < 2:
        offset = 5
    else:
        offset = 10

    if direction == "CALL":
        return base - offset
    else:
        return base + offset

# =========================
# منطق التداول
# =========================
def trading_logic():

    last_signal = None
    entry_price = None
    stage = 0
    profit_step = 100

    send("🚀 SPX Ultimate Options Bot 👿")

    while True:
        try:
            candles = get_spx_data()

            if len(candles) < 30:
                time.sleep(60)
                continue

            closes = [c["close"] for c in candles]
            volumes = [c["volume"] for c in candles]

            ema9 = ema(closes, 9)
            ema21 = ema(closes, 21)

            current_price = closes[-1]
            current_volume = volumes[-1]
            avg_volume = sum(volumes[-10:-1]) / 9

            recent_high = max(closes[-6:-1])
            recent_low = min(closes[-6:-1])

            strong_volume = current_volume > avg_volume * 1.3

            ema_gap = abs(ema9[-1] - ema21[-1])
            volume_strength = current_volume / avg_volume
            break_strength = abs(current_price - recent_high) if ema9[-1] > ema21[-1] else abs(current_price - recent_low)

            strength_score = (ema_gap * 2) + volume_strength + (break_strength / 2)

            # =========================
            # دخول صفقة
            # =========================
            if stage == 0:

                # BUY
                if ema9[-1] > ema21[-1] and current_price > recent_high and strong_volume:
                    strike = choose_strike(current_price, strength_score, "CALL")
                    send(f"🚀 CALL SPX\nStrike: {strike}\nEntry: {current_price}")
                    last_signal = "BUY"
                    entry_price = current_price
                    stage = 1

                # SELL
                elif ema9[-1] < ema21[-1] and current_price < recent_low and strong_volume:
                    strike = choose_strike(current_price, strength_score, "PUT")
                    send(f"🔻 PUT SPX\nStrike: {strike}\nEntry: {current_price}")
                    last_signal = "SELL"
                    entry_price = current_price
                    stage = 1

            # =========================
            # إدارة الصفقة
            # =========================
            if stage == 1:

                if last_signal == "BUY":
                    profit = current_price - entry_price
                else:
                    profit = entry_price - current_price

                if profit >= 100 and profit < 200:
                    send("💰 +100 نقطة → اغلق جزئي")
                elif profit >= 200 and profit < 300:
                    send("💰 +200 نقطة → حرك الوقف")
                elif profit >= 300:
                    send("🏁 +300 نقطة → اغلق كامل الصفقة")
                    stage = 0
                    entry_price = None
                    last_signal = None

            time.sleep(60)

        except Exception as e:
            send(f"❌ خطأ: {e}")
            time.sleep(60)

# =========================
# Flask
# =========================
app = Flask(__name__)

@app.route("/")
def home():
    return "SPX Ultimate Options Bot Running 👿"

def start_thread():
    t = threading.Thread(target=trading_logic)
    t.daemon = True
    t.start()

start_thread()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
