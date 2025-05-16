
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

# Flask-сервер
app = Flask(__name__)

@app.route('/')
def home():
    return "Глечик живий! ✅"

# Файл для запису результатів
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

custom_1330_text = """🔔 13:30 — точка зупинки.
Зупинись на хвилину. Оціни свій стан. Рухайся далі з ясністю, а не інерцією.
"""

evening_text = """🌙 Вечір настав.
Напиши, що ти зробив сьогодні. Наприклад:
Сьогодні: дочитав книгу, зробив 10 присідань, не гортав рілси.

Я збережу і дам флекснутися завтра.
"""

sent_flags = set()

def send_timed_messages():
    now = datetime.utcnow()
    hour = now.hour
    minute = now.minute
    time_key = f"{hour:02}:{minute:02}"

    schedule = {
        "05:00": morning_text,
        "10:30": custom_1330_text,
        "12:00": midday_text,
        "21:00": evening_text
    }

    try:
        if time_key in schedule and time_key not in sent_flags:
            bot.send_message(USER_ID, schedule[time_key])
            logging.info(f"[{time_key}] ✅ Повідомлення надіслано.")
            sent_flags.add(time_key)
        elif time_key not in schedule:
            logging.info(f"[{time_key}] ⏳ Нічого не заплановано.")
    except Exception as e:
        logging.error(f"[{time_key}] ❌ Помилка надсилання: {e}")
    
    print(f"💓 Пінг: {time_key} — бот активний")

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
        time.sleep(60)

if __name__ == '__main__':
    threading.Thread(target=run_bot).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
