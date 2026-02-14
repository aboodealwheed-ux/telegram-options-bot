import os
import requests
import time

TOKEN = os.getenv("TOKEN")
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

print("Bot started with polling...")

last_update_id = None

while True:
    try:
        url = f"{BASE_URL}/getUpdates?timeout=30"
        if last_update_id:
            url += f"&offset={last_update_id + 1}"

        response = requests.get(url).json()

        if response["ok"]:
            for update in response["result"]:
                last_update_id = update["update_id"]

                if "message" in update:
                    chat_id = update["message"]["chat"]["id"]
                    text = update["message"].get("text", "")

                    reply_text = f"🔥 البوت شغال\n\nأرسلت: {text}"

                    requests.post(
                        f"{BASE_URL}/sendMessage",
                        json={
                            "chat_id": chat_id,
                            "text": reply_text
                        }
                    )

    except Exception as e:
        print("Error:", e)

    time.sleep(1)
