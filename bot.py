import telebot
import os
import random
from flask import Flask
from threading import Thread

# 1. Заглушка для Render (чтобы статус был LIVE)
app = Flask('')
@app.route('/')
def home(): return "Бот в сети"
def run(): app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

# 2. Твой токен и ID
TOKEN = "8412093219:AAGmPVtgX1wA133UGsya3UnDf_B5SPphBkM"
bot = telebot.TeleBot(TOKEN)
ADMIN_ID = 7232292366 

db = {} # База балансов

# 3. Начисление денег реплаем (+10000ккк)
@bot.message_handler(func=lambda m: m.reply_to_message and "+10000ккк" in m.text.lower())
def give_money(m):
    if m.from_user.id != ADMIN_ID: return
    tid = m.reply_to_message.from_user.id
    db[tid] = db.get(tid, 0) + 10000000000
    bot.reply_to(m, f"✅ Босс, выдал 10ккк! Баланс игрока: {db[tid]}$")

# 4. Команда /id реплаем
@bot.message_handler(commands=['id'])
def get_id(m):
    uid = m.reply_to_message.from_user.id if m.reply_to_message else m.from_user.id
    bot.reply_to(m, f"🆔 ID: `{uid}`", parse_mode="Markdown")

# 5. Старт и Профиль
@bot.message_handler(commands=['start', 'profile'])
def start(m):
    uid = m.from_user.id
    if uid not in db:
        # Тебе сразу 10ккк при старте, остальным 1000
        db[uid] = 10000000000 if uid == ADMIN_ID else 1000
    bot.reply_to(m, f"🎰 **КАЗИНО**\n💰 Баланс: {db[uid]}$\n\nКоманды: /slots [ставка], /id")

# 6. Слоты
@bot.message_handler(commands=['slots'])
def slots(m):
    uid = m.from_user.id
    try:
        bet = int(m.text.split()[1])
        bal = db.get(uid, 1000)
        if bet > bal or bet <= 0: return bot.reply_to(m, "❌ Мало денег!")
    except: return bot.reply_to(m, "Пиши: /slots 100")
    
    win = random.randint(1, 100) <= 25 # Шанс 25%
    if win: db[uid] += bet * 2
    else: db[uid] -= bet
    bot.reply_to(m, f"{'🎰|🎰|🎰' if win else '🍋|🍒|💎'}\n\n{'✅ Плюс!' if win else '❌ Минус'}")

if __name__ == "__main__":
    Thread(target=run).start()
    bot.infinity_polling()
