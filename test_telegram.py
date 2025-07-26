import requests

# 🔧 مشخصات ربات و کاربر
TELEGRAM_TOKEN = '8253237534:AAFZr4EpriINZtYsuKB2EY4sO7S8Ja52Jhc'
TELEGRAM_CHAT_ID = '5214257544'

# 📨 پیام تست
message = "✅ تست ارسال پیام به تلگرام موفق بود!"

# 🌐 ارسال پیام
def send_telegram_message(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": msg
    }
    response = requests.post(url, data=data)
    print("Status:", response.status_code)
    print("Response:", response.text)

# ▶️ اجرای تابع
send_telegram_message(message)
