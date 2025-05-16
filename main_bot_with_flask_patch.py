# main_bot_with_flask_patch.py

import telebot
from flask import Flask
from threading import Thread
import datetime
import random
import time

TOKEN = "7603422398:AAHb3RCngyJEZXpBINoEHSFcgEQIPXh4ULc"
USER_ID = 493019903

bot = telebot.TeleBot(TOKEN)

# ========== DUMMY FLASK SERVER ==========
app = Flask(__name__)

@app.route('/')
def home():
    return "I’m alive, baby! 💪"

def run_flask():
    app.run(host='0.0.0.0', port=10000)

# ========== BOT LOGIC ==========

messages_sent = set()
points = 0
level = 0

def get_level(points):
    if points >= 100:
        return "Стратег 🌟"
    elif points >= 50:
        return "Боєць 💪"
    elif points >= 20:
        return "Усвідомлений 🤔"
    return "Новачок 👶"

lifehacks = [
    "Пий воду щоранку — мозок буде вдячний 💧",
    "Тримай фокус на одній задачі — багатозадачність це пастка 🎯",
    "Закрий 3 зайві вкладки. Так, ті що зліва 😉",
    "Постав таймер на 25 хвилин і просто почни 🕒",
    "Нема настрою? Поприбирай 5 хвилин — допомагає 🧼"
]

tasks = [
    "Зроби 15 присідань",
    "Вибери товар для перепродажу",
    "Напиши 1 пост для Instagram",
    "Порівняй ціни на товар в 3 магазинах",
    "Зроби 10 віджимань",
    "Додай 1 нову ідею в блокнот",
    "Почни новий Reels або сторіс",
    "Запиши голосову думку щодо нової ніші"
]

@bot.message_handler(commands=['start'])
def start(message):
    if message.chat.id == USER_ID:
        bot.send_message(message.chat.id, "Добрий ранок, глечиче! Я вже на зв’язку 🔥")

@bot.message_handler(commands=['done'])
def mark_done(message):
    global points
    if message.chat.id == USER_ID:
        points += 10
        lvl = get_level(points)
        bot.send_message(message.chat.id, f"✅ Зараховано! У тебе вже {points} балів. Рівень: {lvl}")

# ========== SCHEDULER ==========
last_task_time = None
last_lifehack_time = None

def scheduler():
    global last_task_time, last_lifehack_time
    while True:
        now = datetime.datetime.now()
        time_str = now.strftime("%Y-%m-%d %H:%M")

        if now.hour == 9 and (time_str, "morning") not in messages_sent:
            bot.send_message(USER_ID, "🌞 Добрий ранок! Не залипай, давай фокус 👀")
            messages_sent.add((time_str, "morning"))

        if (last_task_time is None or (now - last_task_time).total_seconds() >= 90 * 60):
            task = random.choice(tasks)
            bot.send_message(USER_ID, f"🎲 Завдання: {task}")
            last_task_time = now

        if (last_lifehack_time is None or (now - last_lifehack_time).total_seconds() >= 60 * 60):
            hack = random.choice(lifehacks)
            bot.send_message(USER_ID, f"🧠 Лайфхак: {hack}")
            last_lifehack_time = now

        time.sleep(30)

# ========== LAUNCH ==========
if __name__ == '__main__':
    Thread(target=run_flask).start()
    Thread(target=scheduler).start()
    bot.polling(none_stop=True)
