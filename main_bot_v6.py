
import logging
import os
import time
import telebot
import random
import json
import requests
from datetime import datetime
from flask import Flask
import threading

# Ініціалізація
logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("BOT_TOKEN")
USER_ID = int(os.getenv("USER_ID"))

# Видалити Webhook
requests.get(f"https://api.telegram.org/bot{TOKEN}/deleteWebhook?drop_pending_updates=true")
bot = telebot.TeleBot(TOKEN)

# Flask для keep-alive
app = Flask(__name__)
@app.route('/')
def home():
    return "Глечик живий! 🚀"

# Дані
HACKS_FILE = "life_hacks.txt"
TASKS_FILE = "tasks.txt"
STATS_FILE = "stats.json"
LOG_FILE = "progress_log.txt"

# Завантажити
with open(HACKS_FILE, encoding="utf-8") as f:
    life_hacks = [line.strip() for line in f if line.strip()]
with open(TASKS_FILE, encoding="utf-8") as f:
    tasks = [line.strip() for line in f if line.strip()]

# Статистика
if os.path.exists(STATS_FILE):
    with open(STATS_FILE, encoding="utf-8") as f:
        stats = json.load(f)
else:
    stats = {"points": 0}

# Зберегти статистику
def save_stats():
    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False)

# Повідомлення
lazy_reasons = [
    "😴 Не знав, з чого почати",
    "📱 Залип у TikTok або рілси",
    "🙁 Не було настрою",
    "😬 Здавалось, що нічого не вийде",
    "🤷 Просто прокрастинація",
    "🔄 Чекав натхнення, але не прийшло"
]

survival_tasks = [
    "📲 Зробити пост у інсту",
    "🏋️ 20 присідань",
    "🛍️ Назвати одну нову ідею для товару",
    "🧠 Записати 3 речі, які тебе порадували сьогодні"
]

motivations = [
    "А ти вже створив акаунт для магазину чи знову тільки меми шариш?",
    "Зроби пост у інсту. Навіть якщо лайкне тільки мама — вже аудиторія.",
    "Поки не створиш магазин — ні одна коробка з товаром сама себе не продасть.",
    "Відтиснись 10 разів. Не від проблем — від підлоги.",
    "10 присідань — не спорт, а заклинання від самобичування.",
    "Повернись до тіла. Воно тобі не мстить, воно просить хоч щось зробити.",
    "Хоч один рух — і ти вже не просто лежиш. Ти — герой каденції.",
]

# Генерація повідомлень
def build_morning_message():
    return f"""🎯 Добрий ранок, глечино!
Сьогодні замість TikTok:
1️⃣ План: випий води
2️⃣ Життєвий хак: {random.choice(life_hacks)}
3️⃣ Справжнє завдання: {random.choice(tasks)}

Напиши /done коли виконаєш — +10 балів."""

def build_survival_message():
    return "💥 *Сьогодні — День виживання!* Виконай усе:
" + "
".join(survival_tasks)

def build_lazy_check():
    return "❓ Що з цього тебе зупинило сьогодні?
" + "
".join(lazy_reasons)

# Час для випадкового мотиватора
random.seed(datetime.now().date().toordinal())
hour = random.randint(12, 17)
minute = random.randint(0, 59)
rand_motivation_time = f"{hour:02d}:{minute:02d}"

# Розклад
messages = {
    "05:00": build_morning_message,
    "14:00": lambda: "🧠 Як настрій по 10-бальній шкалі? (відповідай просто числом)",
    "21:00": lambda: "🌙 Вечір настав. Напиши, що зробив сьогодні через /done:

" + build_lazy_check(),
    rand_motivation_time: lambda: random.choice(motivations)
}

# Survival понеділок 09:00
if datetime.utcnow().weekday() == 0:
    messages["09:00"] = build_survival_message

# Стан
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
    if time_key in messages and time_key not in sent_flags:
        text = messages[time_key]()
        bot.send_message(USER_ID, text)
        sent_flags.add(time_key)

# Команди
@bot.message_handler(commands=['done'])
def handle_done(message):
    text = message.text.replace("/done", "").strip()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    if text:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {text}\n")
        stats["points"] += 10
        save_stats()
        level = stats["points"] // 100
        levels = ['Новачок','Стратег','Майстер','Генерал','Легенда']
        reply = f"📝 Записано та +10 балів! Усього: {stats['points']} балів."
        if stats["points"] % 100 == 0:
            reply += f" 🎉 Ти досяг рівня «{levels[level] if level < len(levels) else levels[-1]}»!"
        bot.reply_to(message, reply)
    else:
        bot.reply_to(message, "Напиши, що зробив через /done, наприклад:\n/done зробив ранкову рутину")

@bot.message_handler(commands=['show_today'])
def handle_show_today(message):
    today = datetime.now().strftime("%Y-%m-%d")
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            lines = [l for l in f.readlines() if l.startswith(f"[{today}")]
            msg = "📘 Твої сьогоднішні записи:\n" + "".join(lines) if lines else "Сьогодні ще нічого не записано."
            bot.reply_to(message, msg)

# Потоки
def run_scheduler():
    while True:
        send_timed_messages()
        time.sleep(60)

def run_polling():
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            logging.error(f"Polling error: {e}")
            time.sleep(5)

# Старт
if __name__ == '__main__':
    threading.Thread(target=run_scheduler, daemon=True).start()
    threading.Thread(target=run_polling, daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
