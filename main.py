from flask import Flask
import requests

app = Flask(__name__)

# اطلاعات ربات و چت آیدی — حتماً اینجا توکن جدید رو بذار
BOT_TOKEN = 'توکن_جدید_تو_اینجا'
CHAT_ID = '5214257544'

def send_test_message():
    message = "✅ ربات با موفقیت روی Render اجرا شده!"
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
    payload = {
        'chat_id': CHAT_ID,
        'text': message
    }
    response = requests.post(url, data=payload)
    print("Status code:", response.status_code)
    print("Response:", response.text)

@app.route('/')
def home():
    send_test_message()
    return "Bot is running ✅"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
