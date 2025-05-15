
import logging
import os
import time
import telebot
from datetime import datetime
from flask import Flask
import threading

# Ініціалізація
logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("BOT_TOKEN")
USER_ID = int(os.getenv("USER_ID"))
bot = telebot.TeleBot(TOKEN)

# Flask-сервер для Render
app = Flask(__name__)

@app.route('/')
def home():
    return "Глечик працює! 🧠"

# Лог-файл
LOG_FILE = "progress_log.txt"

# Повідомлення
morning_text = """🎯 Добрий ранок, глечино!
План дій замість TikTok:
1️⃣ Вода
2️⃣ План на день
3️⃣ Мікроуспіх (будь-який)

Напиши /done коли щось виконаєш.
"""

midday_text = """⏳ 15:00.
Ти ще з нами? Якщо ні — кинь TikTok і зроби щось, що зробить тебе гордим.
"""

evening_text = """🌙 Вечір настав.
Напиши, що ти зробив сьогодні. Наприклад:
Сьогодні: дочитав книгу, зробив 10 присідань, не гортав рілси.

Я збережу і дам флекснутися завтра.
"""

def send_timed_messages():
    now = datetime.utcnow()
    hour = now.hour
    day = (now.date() - datetime(2025, 5, 16).date()).days % 7

    try:
        if hour == 5:  # 08:00 за Києвом
            bot.send_message(USER_ID, morning_text)
        elif hour == 12:  # 15:00 за Києвом
            bot.send_message(USER_ID, midday_text)
        elif hour == 21:  # 00:00 за Києвом
            bot.send_message(USER_ID, evening_text)
    except Exception as e:
        logging.error(f"Помилка надсилання повідомлення: {e}")

@bot.message_handler(commands=['done'])
def handle_done(message):
    user_input = message.text.replace("/done", "").strip()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    if user_input:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {user_input}\n")
        bot.reply_to(message, "📝 Записано. Глечик гордий.")
    else:
        bot.reply_to(message, "Напиши після /done, що ти зробив. Наприклад:\n/done зробив ранкову рутину")

@bot.message_handler(commands=['show_today'])
def handle_show_today(message):
    today = datetime.now().strftime("%Y-%m-%d")
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
        today_logs = [line for line in lines if line.startswith(f"[{today}")]
        if today_logs:
            bot.reply_to(message, "📘 Твої сьогоднішні записи:\n" + "".join(today_logs))
        else:
            bot.reply_to(message, "Сьогодні ще нічого не записано. Чекаю перший флекс 💪")
    else:
        bot.reply_to(message, "Лог поки що порожній.")

def run_bot():
    while True:
        send_timed_messages()
        time.sleep(3600)

# Запуск
if __name__ == '__main__':
    threading.Thread(target=run_bot).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
