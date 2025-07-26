from flask import Flask
import requests
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import os

app = Flask(__name__)

bot_token = '8253237534:AAFZr4EpriINZtYsuKB2EY4sO7S8Ja52Jhc'
chat_id = '5214257544'

# تنظیمات مرورگر برای گرفتن اسکرین‌شات
def get_screenshot():
    url = "https://www.tradingview.com/chart/"  # لینک مستقیم چارت بیت‌کوین اگر داری جایگزین کن
    options = Options()
    options.headless = True
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    driver.set_window_size(1280, 720)
    driver.get(url)
    screenshot_path = "/tmp/chart.png"
    driver.save_screenshot(screenshot_path)
    driver.quit()
    return screenshot_path

# چاک صعودی یا نزولی
def detect_choch():
    # اینجا باید دیتاهای لایو بیت‌کوین رو بخونی
    # فعلاً شبیه‌سازی‌شده:
    current_price = 100001  # فرضی
    if current_price > 100000:
        return "bullish"
    elif current_price < 99900:
        return "bearish"
    else:
        return None

def send_alert(choch_type):
    screenshot = get_screenshot()
    message = f"🚨 CHoCH Detected: {choch_type.upper()} at {datetime.now().strftime('%H:%M:%S')}"
    send_photo_url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
    with open(screenshot, 'rb') as photo:
        files = {'photo': photo}
        data = {'chat_id': chat_id, 'caption': message}
        requests.post(send_photo_url, files=files, data=data)

def monitor():
    choch = detect_choch()
    if choch:
        send_alert(choch)

@app.route('/')
def home():
    return 'Bot is running...'

scheduler = BackgroundScheduler()
scheduler.add_job(monitor, 'interval', minutes=1)
scheduler.start()

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
