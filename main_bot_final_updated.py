
import logging
import os
import time
import telebot
from datetime import datetime
from flask import Flask
import threading

# Налаштування логування
logging.basicConfig(level=logging.INFO)

# Ініціалізація бота
TOKEN = os.getenv("BOT_TOKEN")
USER_ID = int(os.getenv("USER_ID"))
bot = telebot.TeleBot(TOKEN)

# Flask-сервер для keep-alive
app = Flask(__name__)

@app.route('/')
def home():
    return "Глечик живий! 🚀"

# Файл логу прогресу
LOG_FILE = "progress_log.txt"

# Тексти повідомлень
messages = {
    "05:00": """🎯 Добрий ранок, глечино!
План дій замість TikTok:
1️⃣ Вода
2️⃣ План на день
3️⃣ Мікроуспіх (будь-який)

Напиши /done коли щось виконаєш.
""",
    "10:30": """🔔 13:30 — точка зупинки.
Зупинись на хвилину. Оціни свій стан. Рухайся далі з ясністю, а не інерцією.
""",
    "12:53": """⏳ 15:53.
Ти ще з нами? Якщо ні — кинь TikTok і зроби щось, що зробить тебе гордим.
""",
    "14:00": """🔔 17:00 — час перевірити прогрес.
Переглянь список справ і зроби хоча б одну річ із нього.
""",
    "21:00": """🌙 Вечір настав.
Напиши, що ти зробив сьогодні. Наприклад:
Сьогодні: дочитав книгу, зробив 10 присідань, не гортав рілси.

Я збережу і дам флекснутися завтра.
"""
}

# Стан відправлених за день повідомлень
sent_flags = set()
last_day = None

def send_timed_messages():
    global sent_flags, last_day
    now = datetime.utcnow()
    time_key = now.strftime("%H:%M")
    today_day = now.strftime("%Y-%m-%d")

    # Якщо новий день — очищаємо прапорці
    if last_day != today_day:
        sent_flags.clear()
        last_day = today_day
        logging.info(f"📆 Новий день: {today_day}, скинуто sent_flags")

    # Відправка якщо час співпадає і ще не відправляли
    if time_key in messages and time_key not in sent_flags:
        try:
            bot.send_message(USER_ID, messages[time_key])
            logging.info(f"[{time_key}] Повідомлення надіслано")
            sent_flags.add(time_key)
        except Exception as e:
            logging.error(f"[{time_key}] Помилка надсилання: {e}")
    else:
        logging.info(f"[{time_key}] Нічого не заплановано або вже надіслано")

    # Пінг у консоль, щоб бачити активність
    print(f"💓 Пінг: {time_key} — бот активний")

# Обробка команди /done
@bot.message_handler(commands=['done'])
def handle_done(message):
    user_input = message.text.replace("/done", "").strip()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    if user_input:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {user_input}
")
        bot.reply_to(message, "📝 Записано. Глечик гордий.")
    else:
        bot.reply_to(message, "Напиши після /done, що ти зробив. Наприклад:
/done зробив ранкову рутину")

# Обробка команди /show_today
@bot.message_handler(commands=['show_today'])
def handle_show_today(message):
    today = datetime.now().strftime("%Y-%m-%d")
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
        today_logs = [line for line in lines if line.startswith(f"[{today}")]
        if today_logs:
            bot.reply_to(message, "📘 Твої сьогоднішні записи:
" + "".join(today_logs))
        else:
            bot.reply_to(message, "Сьогодні ще нічого не записано. Чекаю перший флекс 💪")
    else:
        bot.reply_to(message, "Лог поки що порожній.")

# Thread для шедулера
def run_scheduler():
    while True:
        send_timed_messages()
        time.sleep(60)

# Thread для polling команд
def run_polling():
    bot.polling(none_stop=True)

# Старт сервісу
if __name__ == '__main__':
    threading.Thread(target=run_scheduler, daemon=True).start()
    threading.Thread(target=run_polling, daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
