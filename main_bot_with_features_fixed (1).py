
import logging
import os
import time
import telebot
import random
import json
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

# Файли даних
HACKS_FILE = "life_hacks.txt"
TASKS_FILE = "tasks.txt"
STATS_FILE = "stats.json"
LOG_FILE = "progress_log.txt"

# Завантаження life-hacks і tasks
with open(HACKS_FILE, encoding="utf-8") as f:
    life_hacks = [line.strip() for line in f if line.strip()]
with open(TASKS_FILE, encoding="utf-8") as f:
    tasks = [line.strip() for line in f if line.strip()]

# Ініціалізація статистики
if os.path.exists(STATS_FILE):
    with open(STATS_FILE, encoding="utf-8") as f:
        stats = json.load(f)
else:
    stats = {"points": 0}

# Функція збереження статистики
def save_stats():
    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False)

# Тексти базових повідомлень
def build_morning_message():
    hack = random.choice(life_hacks)
    task = random.choice(tasks)
    return f"""🎯 Добрий ранок, глечино!
Сьогодні замість TikTok:
1️⃣ План: випий води
2️⃣ Життєвий хак: {hack}
3️⃣ Справжнє завдання: {task}

Напиши /done коли виконаєш — +10 балів.
"""

evening_text = """🌙 Вечір настав.
Напиши, що ти зробив сьогодні через /done:
"""

# Розклад повідомлень
messages = {
    "05:00": build_morning_message,
    "10:30": lambda: "🔔 13:30 — точка зупинки.
Оцінити стан.",
    "12:53": lambda: "⏳ 15:53.
Ти ще з нами? Якщо ні — кинь TikTok і зроби щось, що зробить тебе гордим.",
    "14:00": lambda: "🔔 17:00 — час перевірити прогрес.
Переглянь список справ і зроби хоча б одну річ із нього.",
    "21:00": lambda: evening_text
}

# Зберігати стани відправлених повідомлень
sent_flags = set()
last_day = None

def send_timed_messages():
    global sent_flags, last_day
    now = datetime.utcnow()
    time_key = now.strftime("%H:%M")
    today = now.strftime("%Y-%m-%d")

    # Якщо новий день — очищаємо прапорці
    if last_day != today:
        sent_flags.clear()
        last_day = today
        logging.info(f"[{today}] Новий день, очищено sent_flags.")

    # Відправка повідомлення
    if time_key in messages and time_key not in sent_flags:
        text = messages[time_key]()
        bot.send_message(USER_ID, text)
        sent_flags.add(time_key)
        logging.info(f"[{time_key}] Повідомлення надіслано.")
    else:
        logging.info(f"[{time_key}] Ніяких повідомлень або вже надіслано.")

# Обробка команди /done
@bot.message_handler(commands=['done'])
def handle_done(message):
    text = message.text.replace("/done", "").strip()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    if text:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {text}\n")
        old_points = stats.get("points", 0)
        stats["points"] = old_points + 10
        save_stats()
        old_level = old_points // 100
        new_level = stats["points"] // 100
        reply = f"📝 Записано та +10 балів! Усього: {stats['points']} балів."
        levels = ['Новачок','Стратег','Майстер','Генерал','Легенда']
        if new_level > old_level:
            lvl_name = levels[new_level] if new_level < len(levels) else levels[-1]
            reply += f" 🎉 Вітаю! Ти досяг рівня «{lvl_name}»!"
        bot.reply_to(message, reply)
    else:
        bot.reply_to(message, "Напиши, що зробив через /done, наприклад:
/done зробив ранкову рутину")

# Обробка команди /show_today
@bot.message_handler(commands=['show_today'])
def handle_show_today(message):
    today = datetime.now().strftime("%Y-%m-%d")
    logs = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            logs = f.readlines()
    today_logs = [ln for ln in logs if ln.startswith(f"[{today}")]
    if today_logs:
        bot.reply_to(message, "📘 Твої сьогоднішні записи:
" + "".join(today_logs))
    else:
        bot.reply_to(message, "Сьогодні ще нічого не записано.")

# Scheduler and polling
def run_scheduler():
    while True:
        send_timed_messages()
        time.sleep(60)

def run_polling():
    bot.polling(none_stop=True)

if __name__ == '__main__':
    threading.Thread(target=run_scheduler, daemon=True).start()
    threading.Thread(target=run_polling, daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
