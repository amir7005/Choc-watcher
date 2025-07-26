import ccxt
import pandas as pd
import requests
import time
from flask import Flask
from datetime import datetime
import io
from PIL import Image
import matplotlib.pyplot as plt

# ================= تنظیمات ==================
# اطلاعات شخصی شما
bot_token = '8253237534:AAFZr4EpriINZtYsuKB2EY4sO7S8Ja52Jhc'
chat_id = '5214257544'
render_api_key = 'rnd_TjXiPj1lnwQGLdOajZPXa7xvN7nT'
service_id = 'srv-d22aspre5dus739es2o0'

# ارسال دکمه‌های کنترل به تلگرام
def send_control_buttons():
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": "⚙️ لطفاً یکی از گزینه‌های زیر را انتخاب کنید:",
        "reply_markup": {
            "inline_keyboard": [
                [{"text": "🛑 توقف هشدارها", "callback_data": "stop_service"}],
                [{"text": "✅ فعال‌سازی هشدارها", "callback_data": "start_service"}]
            ]
        }
    }
    requests.post(url, json=payload)

# توقف سرویس در Render
def stop_render_service():
    url = f"https://api.render.com/v1/services/{service_id}/suspend"
    headers = {
        "Authorization": f"Bearer {render_api_key}",
        "Accept": "application/json"
    }
    requests.post(url, headers=headers)

# اجرای مجدد سرویس در Render
def start_render_service():
    url = f"https://api.render.com/v1/services/{service_id}/resume"
    headers = {
        "Authorization": f"Bearer {render_api_key}",
        "Accept": "application/json"
    }
    requests.post(url, headers=headers)

# هندل Webhook تلگرام
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json

    if "callback_query" in data:
        callback = data["callback_query"]
        user_id = str(callback["from"]["id"])
        data_text = callback["data"]
        message_id = callback["message"]["message_id"]

        if user_id != chat_id:
            return "Unauthorized", 403

        if data_text == "stop_service":
            stop_render_service()
            reply_text = "⛔ هشدارها متوقف شدند."
        elif data_text == "start_service":
            start_render_service()
            reply_text = "✅ هشدارها فعال شدند."
        else:
            reply_text = "دستور نامعتبر است."

        # پاسخ به کلیک دکمه
        requests.post(f"https://api.telegram.org/bot{bot_token}/answerCallbackQuery", data={
            "callback_query_id": callback["id"]
        })

        # ویرایش متن پیام
        requests.post(f"https://api.telegram.org/bot{bot_token}/editMessageText", json={
            "chat_id": chat_id,
            "message_id": message_id,
            "text": reply_text
        })

    return "ok", 200

@app.route('/')
def index():
    return '✅ Webhook Active'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)

send_control_buttons()
