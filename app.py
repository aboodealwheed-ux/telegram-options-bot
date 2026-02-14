@app.route("/", methods=["POST"])
def webhook():
    global CHAT_ID

    data = request.get_json(force=True)

    print("Incoming update:", data)

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if text == "/start":
            send_message_to(chat_id, "🔥 تم تشغيل البوت بنجاح")

        else:
            send_message_to(chat_id, "📡 البوت يعمل حالياً")

    return "ok"
