import ccxt
import pandas as pd
import requests
import time
from datetime import datetime
import io
from PIL import Image
import matplotlib.pyplot as plt
from flask import Flask, request
import requests
import json

app = Flask(__name__)  # ← این خط مهمه

# -------- تنظیمات --------
bot_token = "8253237534:AAFZr4EpriINZtYsuKB2EY4sO7S8Ja52Jhc"
chat_id = "5214257544"
render_api_key = "rnd_TjXiPj1lnwQGLdOajZPXa7xvN7nT"
render_service_id = "srv-d22aspre5dus739es2o0"

# -------- پیام ساده به تلگرام --------
def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    requests.post(url, data=payload)

# -------- ارسال دکمه‌ها به تلگرام --------
def send_buttons():
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    keyboard = {
        "inline_keyboard": [
            [
                {"text": "🛑 توقف هشدارها", "callback_data": "stop"},
                {"text": "✅ فعال‌سازی هشدارها", "callback_data": "start"}
            ]
        ]
    }
    payload = {
        "chat_id": chat_id,
        "text": "مدیریت وضعیت هشدارها:",
        "reply_markup": json.dumps(keyboard)
    }
    requests.post(url, data=payload)

# -------- کنترل سرویس Render --------
def start_render_service():
    url = f"https://api.render.com/v1/services/{render_service_id}/resume"
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {render_api_key}"
    }
    response = requests.put(url, headers=headers)
    return response.status_code == 200

def stop_render_service():
    url = f"https://api.render.com/v1/services/{render_service_id}/suspend"
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {render_api_key}"
    }
    response = requests.put(url, headers=headers)
    return response.status_code == 200

# -------- Webhook برای دکمه‌ها --------
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json

    if 'callback_query' in data:
        query = data['callback_query']
        data_value = query['data']

        if data_value == 'stop':
            if stop_render_service():
                send_telegram_message("🔴 هشدارها غیرفعال شد (سرویس متوقف شد).")
            else:
                send_telegram_message("⚠️ خطا در توقف سرویس Render.")

        elif data_value == 'start':
            if start_render_service():
                send_telegram_message("🟢 هشدارها فعال شد (سرویس راه‌اندازی شد).")
            else:
                send_telegram_message("⚠️ خطا در فعال‌سازی سرویس Render.")

        # پاسخ به تلگرام که دکمه کلیک شده
        requests.post(f"https://api.telegram.org/bot{bot_token}/answerCallbackQuery",
                      data={"callback_query_id": query["id"]})

    return 'OK'

# -------- تست اولیه هنگام اجرا --------
@app.route('/')
def index():
    send_telegram_message("✅ سرور راه‌اندازی شد.")
    send_buttons()
    return 'Bot is running!'

# -------- اجرا --------
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=10000)
