from flask import Flask
import requests
import os

app = Flask(__name__)

# این تابع برای تست ارسال پیام تلگرامه
def send_telegram_message(message):
    bot_token = '8253237534:AAFZr4EpriINZtYsuKB2EY4sO7S8Ja52Jhc'
    chat_id = '5214257544'
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    try:
        res = requests.post(url, json=payload)
        print("Telegram response:", res.text)
    except Exception as e:
        print("Telegram Error:", e)

@app.route('/')
def index():
    return 'Bot is running.'

@app.route('/test')
def test():
    send_telegram_message("✅ تست موفق بود! بات کار می‌کنه.")
    return 'Test message sent!'

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
