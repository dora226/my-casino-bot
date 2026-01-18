import telebot
import os
import random
from flask import Flask
from threading import Thread

# --- БЛОК ДЛЯ RENDER (ЧТОБЫ РАБОТАЛО БЕСПЛАТНО) ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run():
    # Render дает порт в переменных окружения, либо используем 10000
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

keep_alive()
# --------------------------------------------------

# ТВОЙ ТОКЕН (Замени на новый из BotFather, если ошибка 409 останется)
TOKEN = "6150422667:AA..." 
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🎰 Казино запущено и работает на Render!")

# Сюда вставь остальную логику своего казино (игры, ранги и т.д.)

if __name__ == "__main__":
    bot.infinity_polling()
