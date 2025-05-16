
import telebot

TOKEN = "7603422398:AAHb3RCngyJEZXpBINoEHSFcgEQIPXh4ULc"
USER_ID = 493019903

bot = telebot.TeleBot(TOKEN)
bot.remove_webhook()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(USER_ID, "Бот запущено успішно, глечино!")

bot.polling()
