import ccxt
import pandas as pd
import requests
import time
from flask import Flask
from datetime import datetime
import io
from PIL import Image
import matplotlib.pyplot as plt

# اطلاعات ربات تلگرام
bot_token = '8253237534:AAFZr4EpriINZtYsuKB2EY4sO7S8Ja52Jhc'
chat_id = '5214257544'

# تابع ارسال پیام به تلگرام
def send_telegram_message(message):
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    payload = {'chat_id': chat_id, 'text': message}
    requests.post(url, data=payload)

# تابع ارسال تصویر به تلگرام
def send_telegram_photo(image_bytes):
    url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
    files = {"photo": ("chart.png", image_bytes)}
    data = {"chat_id": chat_id}
    requests.post(url, files=files, data=data)

# تابع دریافت داده کندل از Binance
def fetch_ohlcv():
    exchange = ccxt.binance()
    symbol = 'BTC/USDT'
    timeframe = '1m'
    limit = 100
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df

# تابع تشخیص چاک (Change of Character)
def check_change_of_character(df, direction="bullish"):
    if len(df) < 5:
        return False

    last_high = df['high'].iloc[-2]
    last_low = df['low'].iloc[-2]

    if direction == "bullish":
        # تشخیص شکست آخرین سقف در روند نزولی
        if last_high > max(df['high'].iloc[-5:-2]):
            return True

    if direction == "bearish":
        # تشخیص شکست آخرین کف در روند صعودی
        if last_low < min(df['low'].iloc[-5:-2]):
            return True

    return False

# رسم چارت و ارسال تصویر به تلگرام
def take_screenshot_and_send():
    df = fetch_ohlcv()
    plt.figure(figsize=(10, 4))
    plt.plot(df['timestamp'], df['close'], label='Close Price')
    plt.title('BTC/USDT - 1m')
    plt.xlabel('Time')
    plt.ylabel('Price')
    plt.grid(True)
    plt.tight_layout()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    send_telegram_photo(buf)
    plt.close()

# بررسی بازار و ارسال هشدار
def monitor():
    while True:
        try:
            df = fetch_ohlcv()
            bullish_chak = check_change_of_character(df, direction="bullish")
            bearish_chak = check_change_of_character(df, direction="bearish")

            if bullish_chak:
                send_telegram_message("📈 CHoCH Bullish Detected!")
                take_screenshot_and_send()

            if bearish_chak:
                send_telegram_message("📉 CHoCH Bearish Detected!")
                take_screenshot_and_send()

        except Exception as e:
            print("Error:", e)

        time.sleep(60)

# اجرای مانیتورینگ در پس‌زمینه روی Render
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Bot is running..."

if __name__ == '__main__':
    import threading
    threading.Thread(target=monitor).start()
    app.run(host='0.0.0.0', port=10000)
