#Implementation with Telegram Bot API
#Using the Telegram Bot API, you can send the extracted_text as a new message:

import requests

BOT_TOKEN = 'your_bot_token'
CHAT_ID = 'your_chat_id'

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)

# Simulating extracted text from an image
extracted_text = "This is the extracted text from the image."

# Re-send as a new message
send_message(CHAT_ID, extracted_text)
