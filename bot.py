import telebot
import os
import random
from flask import Flask
from threading import Thread

# 1. Веб-сервер для обхода ошибки Port на Render
app = Flask('')

@app.route('/')
def home():
    return "Бот запущен и работает!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# 2. Настройки бота
TOKEN = "8412093219:AAErKd0JNLUHQceK9SFxEND8N4FzyCW9WBg"
bot = telebot.TeleBot(TOKEN)
ADMIN_ID = 6150422667 

db = {} # База данных балансов

# 3. Админ-функция: +10000ккк реплаем
@bot.message_handler(func=lambda m: m.reply_to_message and "+10000ккк" in m.text.lower())
def give_money(m):
    if m.from_user.id != ADMIN_ID: return
    target = m.reply_to_message.from_user.id
    db[target] = db.get(target, 0) + 10000000000
    bot.reply_to(m, f"💰 Босс, начислил! Текущий баланс: {db[target]}$")

# 4. Команда /id (реплаем или просто так)
@bot.message_handler(commands=['id'])
def get_id(m):
    target = m.reply_to_message.from_user.id if m.reply_to_message else m.from_user.id
    bot.reply_to(m, f"🆔 ID пользователя: `{target}`", parse_mode="Markdown")

# 5. Профиль и Слоты
@bot.message_handler(commands=['start', 'profile'])
def profile(m):
    uid = m.from_user.id
    if uid not in db: db[uid] = 1000
    bot.reply_to(m, f"🎰 **КАЗИНО**\n\n🔹 Твой ID: `{uid}`\n💰 Баланс: {db[uid]}$\n\n🎮 Игры: /slots [ставка]", parse_mode="Markdown")

@bot.message_handler(commands=['slots'])
def slots(m):
    uid = m.from_user.id
    try:
        parts = m.text.split()
        if len(parts) < 2: return bot.reply_to(m, "Введите ставку: `/slots 100`", parse_mode="Markdown")
        bet = int(parts[1])
        bal = db.get(uid, 1000)
        if bet > bal or bet <= 0: return bot.reply_to(m, "❌ Недостаточно средств!")
    except: return bot.reply_to(m, "Ошибка! Введите число.")

    # Шанс на победу 25%
    win = random.randint(1, 100) <= 25
    if win:
        db[uid] = bal + (bet * 2)
        res = f"🎰|🎰|🎰\n\n🔥 ПОБЕДА! +{bet * 2}$"
    else:
        db[uid] = bal - bet
        res = f"🍋|🍒|💎\n\n📉 ПРОИГРЫШ. -{bet}$"
    
    bot.reply_to(m, f"{res}\n💰 Баланс: {db[uid]}$")

# 6. Запуск сервера и бота
if __name__ == "__main__":
    # Запускаем Flask в отдельном потоке
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()
    
    # Запускаем бота
    print("Бот погнал...")
    bot.infinity_polling(timeout=20, long_polling_timeout=10)
