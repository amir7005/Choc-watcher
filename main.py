from flask import Flask, request
import requests
import json
import os

app = Flask(__name__)

# اطلاعات ربات تلگرام
bot_token = '8253237534:AAFZr4EpriINZtYsuKB2EY4sO7S8Ja52Jhc'
chat_id = '5214257544'

# اطلاعات API سرویس Render
render_service_id = 'srv-d22aspre5dus739es2o0'  # باید از داشبورد Render بگیری
render_api_key = 'rnd_TjXiPj1lnwQGLdOajZPXa7xvN7nT'  # توکن API اختصاصی خودت

# ارسال پیام متنی

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text
    }
    requests.post(url, data=payload)

# ارسال دکمه‌های کیبورد ثابت

def send_buttons():
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    keyboard = {
        "keyboard": [
            [{"text": "🛑 توقف هشدارها"}, {"text": "✅ فعال‌سازی هشدارها"}]
        ],
        "resize_keyboard": True,
        "one_time_keyboard": False
    }
    payload = {
        "chat_id": chat_id,
        "text": "از دکمه‌ها برای مدیریت هشدار استفاده کنید:",
        "reply_markup": json.dumps(keyboard)
    }
    requests.post(url, data=payload)

# توقف سرویس Render

def stop_render_service():
    url = f"https://api.render.com/v1/services/{render_service_id}/pause"
    headers = {
        'Authorization': f'Bearer {render_api_key}',
        'Accept': 'application/json'
    }
    response = requests.post(url, headers=headers)
    return response.status_code == 200

# راه‌اندازی مجدد سرویس Render

def start_render_service():
    url = f"https://api.render.com/v1/services/{render_service_id}/resume"
    headers = {
        'Authorization': f'Bearer {render_api_key}',
        'Accept': 'application/json'
    }
    response = requests.post(url, headers=headers)
    return response.status_code == 200

# Webhook برای دریافت پیام از ربات

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json

    if 'message' in data:
        message_text = data['message'].get('text', '')

        if message_text == '🛑 توقف هشدارها':
            if stop_render_service():
                send_telegram_message("🔴 هشدارها غیرفعال شد (سرویس متوقف شد).")
            else:
                send_telegram_message("⚠️ خطا در توقف سرویس Render.")

        elif message_text == '✅ فعال‌سازی هشدارها':
            if start_render_service():
                send_telegram_message("🟢 هشدارها فعال شد (سرویس راه‌اندازی شد).")
            else:
                send_telegram_message("⚠️ خطا در فعال‌سازی سرویس Render.")

    return 'OK'

@app.route('/')
def index():
    send_buttons()
    return 'ربات فعال است ✅'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
