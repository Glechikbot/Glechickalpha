
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
bot = telebot.TeleBot(TOKEN)
bot.remove_webhook()  # видаляємо будь-який старий webhook
USER_ID = int(os.getenv("USER_ID"))

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

# Завантаження даних
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

def save_stats():
    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False)

def build_morning_message():
    hack = random.choice(life_hacks)
    task = random.choice(tasks)
    return (f"🎯 Добрий ранок, глечино!\n"
            f"Сьогодні замість TikTok:\n"
            f"1️⃣ План: випий води\n"
            f"2️⃣ Життєвий хак: {hack}\n"
            f"3️⃣ Справжнє завдання: {task}\n\n"
            f"Напиши /done коли виконаєш — +10 балів.")

evening_text = "🌙 Вечір настав.\nНапиши, що ти зробив сьогодні через /done:"

messages = {
    "05:00": build_morning_message,
    "10:30": lambda: "🔔 13:30 — точка зупинки.\nОцінити стан.",
    "12:53": lambda: "⏳ 15:53.\nТи ще з нами? Якщо ні — кинь TikTok і зроби щось, що зробить тебе гордим.",
    "14:00": lambda: "🔔 17:00 — час перевірити прогрес.\nПереглянь список справ і зроби хоча б одну річ із нього.",
    "21:00": lambda: evening_text
}

sent_flags = set()
last_day = None

def send_timed_messages():
    global sent_flags, last_day
    now = datetime.utcnow()
    time_key = now.strftime("%H:%M")
    today = now.strftime("%Y-%m-%d")
    if last_day != today:
        sent_flags.clear()
        last_day = today
        logging.info(f"[{today}] Новий день, очищено sent_flags.")
    if time_key in messages and time_key not in sent_flags:
        text = messages[time_key]()
        bot.send_message(USER_ID, text)
        sent_flags.add(time_key)
        logging.info(f"[{time_key}] Повідомлення надіслано.")
    else:
        logging.info(f"[{time_key}] Нічого не заплановано або вже надіслано.")

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
        bot.reply_to(message, "Напиши, що зробив через /done, наприклад:\n/done зробив ранкову рутину")

@bot.message_handler(commands=['show_today'])
def handle_show_today(message):
    today = datetime.now().strftime("%Y-%m-%d")
    logs = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            logs = f.readlines()
    today_logs = [ln for ln in logs if ln.startswith(f"[{today}")]
    if today_logs:
        bot.reply_to(message, "📘 Твої сьогоднішні записи:\n" + "".join(today_logs))
    else:
        bot.reply_to(message, "Сьогодні ще нічого не записано.")

def run_scheduler():
    while True:
        send_timed_messages()
        time.sleep(60)

def run_polling():
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            logging.error(f"Polling error: {e}, перезапуск через 5 сек...")
            time.sleep(5)

if __name__ == '__main__':
    threading.Thread(target=run_scheduler, daemon=True).start()
    threading.Thread(target=run_polling, daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
