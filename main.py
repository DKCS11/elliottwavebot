@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def telegram_webhook():
    data = request.get_json()
    print("Received update:", data)  # optional logging

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        message_text = data["message"].get("text", "")
        reply = generate_reply(message_text)

        try:
            res = requests.post(TELEGRAM_API_URL + "sendMessage", json={
                "chat_id": chat_id,
                "text": reply
            }, timeout=3)  # <= Add timeout
            print("Telegram response:", res.status_code, res.text)
        except Exception as e:
            print("Failed to send reply:", e)

    return {"ok": True}

