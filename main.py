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
bot_token = '8253237534:AAFZr4EpriINZtYsuKB2EY4sO7S8Ja52Jhc'
chat_id = '5214257544'

# ============================================
app = Flask(__name__)

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

    bearish = df['lower_high'].iloc[-3] and df['lower_low'].iloc[-3] and df['high'].iloc[-1] > df['high'].iloc[-3]
    bullish = df['higher_high'].iloc[-3] and df['higher_low'].iloc[-3] and df['low'].iloc[-1] < df['low'].iloc[-3]

    if bullish:
        return 'bullish'
    elif bearish:
        return 'bearish'
    return None

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {'chat_id': chat_id, 'text': message}
    requests.post(url, data=payload)

def plot_chart(df):
    plt.figure(figsize=(10, 5))
    plt.plot(df['close'], label='Close Price', color='blue')
    plt.title('BTC/USDT - 1m Chart')
    plt.xlabel('Candle Index')
    plt.ylabel('Price (USDT)')
    plt.grid(True)
    plt.legend()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()
    return buf

def send_photo_telegram(photo_buf):
    url = f'https://api.telegram.org/bot{bot_token}/sendPhoto'
    files = {'photo': ('chart.png', photo_buf)}
    data = {'chat_id': chat_id}
    requests.post(url, files=files, data=data)

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
                chart_img = plot_chart(df)
                send_photo_telegram(chart_img)
                last_signal = signal
        except Exception as e:
            print('❌ خطا:', e)
        time.sleep(60)  # بررسی هر 60 ثانیه

if __name__ == '__main__':
    threading.Thread(target=monitor).start()
    app.run(host='0.0.0.0', port=10000)
