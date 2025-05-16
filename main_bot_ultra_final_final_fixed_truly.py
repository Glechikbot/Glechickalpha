import telebot
import random
import datetime

TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
bot = telebot.TeleBot(TOKEN)

tasks = [
    "Зроби 10 присідань 💪",
    "Порівняй ціни на товар для продажу 🛒",
    "Створи пост для інстаграму про продукт 📸",
    "Зроби 10 віджимань 🏋️",
    "Обери товар з високим попитом 📦"
]

lifehacks = [
    "Замінюй TikTok на стакан води — мозок подякує 🧠",
    "Запиши план дня ще до першого рілса 📃",
    "Вимкни сповіщення на годину і стань вільним 🚫📱"
]

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, "Привіт, глечино! Готовий до продуктивного дня? 🌞")

@bot.message_handler(commands=['done'])
def done_message(message):
    with open("progress.txt", "a") as f:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        f.write(f"{timestamp} {message.text}\n")
    bot.send_message(message.chat.id, "Записано! ✅")

def send_morning_reminder():
    bot.send_message(YOUR_USER_ID, "🚨 Доброго ранку, глечино! Не залипай в телефон, зроби щось із плану!")

def send_random_task():
    task = random.choice(tasks)
    bot.send_message(YOUR_USER_ID, f"🎯 Завдання: {task}")

def send_random_lifehack():
    hack = random.choice(lifehacks)
    bot.send_message(YOUR_USER_ID, f"💡 Лайфхак дня: {hack}")

bot.polling()