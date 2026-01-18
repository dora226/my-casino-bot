import telebot
import os
import random
from flask import Flask
from threading import Thread

# 1. Веб-сервер для статуса LIVE на Render
app = Flask('')
@app.route('/')
def home(): return "Бот работает!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# 2. Настройки (берем токен из Environment Variables)
TOKEN = os.environ.get("BOT_TOKEN") 
bot = telebot.TeleBot(TOKEN)
ADMIN_ID = 6150422667 

db = {}

# 3. Функции: Выдача денег и ID
@bot.message_handler(func=lambda m: m.reply_to_message and "+10000ккк" in m.text.lower())
def give_money(m):
    if m.from_user.id != ADMIN_ID: return
    tid = m.reply_to_message.from_user.id
    db[tid] = db.get(tid, 0) + 10000000000
    bot.reply_to(m, f"✅ Выдано 10ккк! Баланс: {db[tid]}$")

@bot.message_handler(commands=['id'])
def get_id(m):
    uid = m.reply_to_message.from_user.id if m.reply_to_message else m.from_user.id
    bot.reply_to(m, f"🆔 ID: `{uid}`", parse_mode="Markdown")

# 4. Команды игрока
@bot.message_handler(commands=['start', 'profile'])
def start(m):
    uid = m.from_user.id
    if uid not in db: db[uid] = 1000
    bot.reply_to(m, f"🎰 **КАЗИНО**\n💰 Баланс: {db[uid]}$\n\n/slots [ставка]")

@bot.message_handler(commands=['slots'])
def slots(m):
    uid = m.from_user.id
    try:
        bet = int(m.text.split()[1])
        if bet > db.get(uid, 1000) or bet <= 0: return bot.reply_to(m, "❌ Мало денег")
    except: return bot.reply_to(m, "Пример: /slots 100")
    
    win = random.randint(1, 100) <= 25
    if win: db[uid] += bet * 2
    else: db[uid] -= bet
    bot.reply_to(m, f"{'🎰|🎰|🎰' if win else '🍋|🍒|💎'}\n\n{'✅ Плюс!' if win else '❌ Минус'}")

# 5. Запуск
if __name__ == "__main__":
    Thread(target=run_flask, daemon=True).start()
    print("Бот запускается...")
    bot.infinity_polling()
