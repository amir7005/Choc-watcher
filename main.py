import ccxt
import pandas as pd
import requests
import time
from flask import Flask
from datetime import datetime
import io
from PIL import Image
import matplotlib.pyplot as plt

app = Flask(__name__)

# اطلاعات ربات تلگرام
bot_token = '8253237534:AAFZr4EpriINZtYsuKB2EY4sO7S8Ja52Jhc'
chat_id = '5214257544'
screenshot_api_key = 'ATF0ER9-CB64RHQ-PF3D365-4TFA8JP'

def get_ohlcv(symbol="BTC/USDT", timeframe="1m", limit=100):
    exchange = ccxt.binance()
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    return df

def detect_change_of_character(df):
    df['high_shifted'] = df['high'].shift(1)
    df['low_shifted'] = df['low'].shift(1)

    df['lower_high'] = df['high'] < df['high_shifted']
    df['lower_low'] = df['low'] < df['low_shifted']
    df['higher_high'] = df['high'] > df['high_shifted']
    df['higher_low'] = df['low'] > df['low_shifted']

    bearish_condition = df['lower_high'].iloc[-3] and df['lower_low'].iloc[-3] and df['high'].iloc[-1] > df['high'].iloc[-3]
    bullish_condition = df['higher_high'].iloc[-3] and df['higher_low'].iloc[-3] and df['low'].iloc[-1] < df['low'].iloc[-3]

    if bullish_condition:
        return 'bullish'
    elif bearish_condition:
        return 'bearish'
    return None

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {'chat_id': chat_id, 'text': message}
    requests.post(url, data=payload)

def send_screenshot_to_telegram():
    chart_url = 'https://www.tradingview.com/chart/?symbol=BINANCE:BTCUSDT'
    screenshot_url = f'https://api.screenshotapi.net/screenshot?token={screenshot_api_key}&url={chart_url}&full_page=true'
    response = requests.get(screenshot_url)
    data = response.json()

    if 'screenshot' in data:
        image_url = data['screenshot']
        telegram_url = f'https://api.telegram.org/bot{bot_token}/sendPhoto'
        requests.post(telegram_url, data={'chat_id': chat_id, 'photo': image_url})
    else:
        print('❌ خطا در دریافت اسکرین‌شات:', data)

@app.route('/')
def index():
    return 'Bot is running ✅'

def monitor():
    last_signal = None
    while True:
        try:
            df = get_ohlcv()
            signal = detect_change_of_character(df)
            if signal and signal != last_signal:
                send_telegram_message(f"🚨 تغییر روند {signal.upper()} در BTC/USDT")
                send_screenshot_to_telegram()
                last_signal = signal
        except Exception as e:
            print('❌ خطا:', e)

        time.sleep(60)  # هر ۶۰ ثانیه بررسی شود

if __name__ == '__main__':
    import threading
    threading.Thread(target=monitor).start()
    app.run(host='0.0.0.0', port=10000)
