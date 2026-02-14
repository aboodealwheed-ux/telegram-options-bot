import os
import requests
import threading
import time
from datetime import datetime
from zoneinfo import ZoneInfo

import yfinance as yf
import pandas as pd
from flask import Flask, request

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
TELEGRAM_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"
CHAT_ID = None  # سنحفظ آخر شات تواصل معنا

TZ = ZoneInfo("Asia/Riyadh")

SYMBOLS = {
    "SPX": "^GSPC",      # بديل تقريبي (المؤشر الفوري)
    "XAUUSD": "GC=F"     # عقود ذهب
}

SESSION_START = (17, 30)  # 5:30 PM
SESSION_END   = (0, 0)    # 12:00 AM

last_signal = { "SPX": None, "XAUUSD": None }

def in_asia_session():
    now = datetime.now(TZ)
    start = now.replace(hour=SESSION_START[0], minute=SESSION_START[1], second=0, microsecond=0)
    end   = now.replace(hour=SESSION_END[0], minute=SESSION_END[1], second=0, microsecond=0)
    if SESSION_START > SESSION_END:
        return now >= start or now <= end
    return start <= now <= end

def send_message(text):
    if not CHAT_ID:
        return
    requests.post(
        f"{TELEGRAM_URL}/sendMessage",
        json={"chat_id": CHAT_ID, "text": text}
    )

def compute_signal(df15, df5, symbol_name):
    if len(df15) < 10 or len(df5) < 10:
        return None

    # نطاق آخر 8 شموع 15م
    recent = df15.tail(8)
    hi = recent["High"].max()
    lo = recent["Low"].min()
    delta = hi - lo
    if delta == 0:
        return None

    price = df5["Close"].iloc[-1]
    angle = (price - lo) / delta * 90

    # كسر وهمي: خروج ثم عودة داخل النطاق خلال شمعتين 5م
    last5 = df5.tail(3)
    fake_up = last5["High"].max() > hi and price < hi
    fake_dn = last5["Low"].min()  < lo and price > lo

    entry = None
    sl = None
    tp1 = None
    tp2 = None
    side = None

    # شراء قرب القاع + تأكيد عكسي
    if 15 <= angle <= 35 and fake_dn:
        side = "BUY"
        entry = price
        sl = lo - 0.25 * delta
        tp1 = lo + 0.5 * delta
        tp2 = hi

    # بيع قرب القمة + تأكيد عكسي
    if 55 <= angle <= 75 and fake_up:
        side = "SELL"
        entry = price
        sl = hi + 0.25 * delta
        tp1 = hi - 0.5 * delta
        tp2 = lo

    if not side:
        return None

    return {
        "symbol": symbol_name,
        "side": side,
        "entry": round(entry, 2),
        "sl": round(sl, 2),
        "tp1": round(tp1, 2),
        "tp2": round(tp2, 2),
        "angle": round(angle, 1),
        "hi": round(hi, 2),
        "lo": round(lo, 2),
    }

def fetch_data(ticker):
    df15 = yf.download(ticker, interval="15m", period="2d", progress=False)
    df5  = yf.download(ticker, interval="5m",  period="1d", progress=False)
    if df15.empty or df5.empty:
        return None, None
    df15 = df15.dropna()
    df5  = df5.dropna()
    return df15, df5

def worker():
    global last_signal
    while True:
        try:
            if in_asia_session() and CHAT_ID:
                for name, ticker in SYMBOLS.items():
                    df15, df5 = fetch_data(ticker)
                    if df15 is None:
                        continue
                    sig = compute_signal(df15, df5, name)
                    if sig and last_signal.get(name) != sig:
                        last_signal[name] = sig
                        msg = (
                            f"📊 {sig['symbol']} – جلسة آسيا\n"
                            f"الاتجاه: {sig['side']}\n"
                            f"الزاوية: {sig['angle']}°\n"
                            f"النطاق: {sig['lo']} – {sig['hi']}\n\n"
                            f"🎯 دخول: {sig['entry']}\n"
                            f"🛑 وقف: {sig['sl']}\n"
                            f"🎯 هدف1: {sig['tp1']}\n"
                            f"🎯 هدف2: {sig['tp2']}"
                        )
                        send_message(msg)
        except Exception as e:
            print("Error:", e)

        time.sleep(120)  # كل دقيقتين

@app.route("/", methods=["GET"])
def home():
    return "Asia bot running"

@app.route("/", methods=["POST"])
def webhook():
    global CHAT_ID
    data = request.get_json(force=True)
    if "message" in data:
        CHAT_ID = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")
        if text == "/start":
            send_message("🔥 تم تفعيل بوت جلسة آسيا (SPX + Gold)")
        else:
            send_message("📡 شغال.. بانتظار فرص جلسة آسيا.")
    return "ok"

if __name__ == "__main__":
    t = threading.Thread(target=worker, daemon=True)
    t.start()
    app.run(host="0.0.0.0", port=10000)
