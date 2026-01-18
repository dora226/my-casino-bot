import telebot
import os
import random
from flask import Flask
from threading import Thread

# --- БЛОК ДЛЯ RENDER (ЧТОБЫ БОТ НЕ ВЫЛЕТАЛ) ---
app = Flask('')
@app.route('/')
def home(): return "Бот Казино Активен!"
def run():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
def keep_alive():
    t = Thread(target=run, daemon=True)
    t.start()
keep_alive()

# --- НАСТРОЙКИ ---
TOKEN = "8412093219:AAGmPVtgX1wA133UGsya3UnDf_B5SPphBkM"
bot = telebot.TeleBot(TOKEN)
ADMIN_ID = 7232292366 

users = {} 
admin_lucky_mode = True 

def get_bal(uid):
    if uid not in users: users[uid] = 1000
    return users[uid]

@bot.message_handler(commands=['id'])
def get_user_id(message):
    uid = message.reply_to_message.from_user.id if message.reply_to_message else message.from_user.id
    bot.reply_to(message, f"🆔 ID: `{uid}`", parse_mode="Markdown")

@bot.message_handler(commands=['lucky'])
def toggle_lucky(message):
    global admin_lucky_mode
    if message.from_user.id != ADMIN_ID: return
    admin_lucky_mode = not admin_lucky_mode
    bot.reply_to(message, f"🎰 Шанс админа: {'✅ ВКЛ' if admin_lucky_mode else '❌ ВЫКЛ'}")

@bot.message_handler(commands=['start', 'profile'])
def profile(message):
    uid = message.from_user.id
    bal = get_bal(uid)
    text = f"🎰 **КАЗИНО**\n💰 Баланс: {bal}$\n\n/slots [ставка]\n/roulette [ставка] [red/black]"
    if uid == ADMIN_ID: text += f"\n\n👑 Админ-режим: {'ВКЛ' if admin_lucky_mode else 'ВЫКЛ'}"
    bot.reply_to(message, text, parse_mode="Markdown")

@bot.message_handler(commands=['slots'])
def slots(message):
    uid = message.from_user.id
    try:
        bet = int(message.text.split()[1])
        if bet > get_bal(uid) or bet <= 0: return bot.reply_to(message, "❌ Недостаточно денег!")
    except: return bot.reply_to(message, "Пример: /slots 100")

    win = random.randint(1, 100) <= (50 if (uid == ADMIN_ID and admin_lucky_mode) else 15)
    emojis = ["💎", "🎰", "🍒", "7️⃣"]
    res = [random.choice(emojis)] * 3 if win else [random.choice(emojis) for _ in range(3)]
    
    if win: users[uid] += bet * 3
    else: users[uid] -= bet
    bot.reply_to(message, f"| {' | '.join(res)} |\n\n{'🔥 +'+str(bet*3)+'$' if win else '📉 -'+str(bet)+'$'}")

@bot.message_handler(commands=['give'])
def give_money(message):
    if message.from_user.id != ADMIN_ID: return
    args = message.text.split()
    users[int(args[1])] = users.get(int(args[1]), 0) + int(args[2])
    bot.reply_to(message, "✅ Выдано!")

if __name__ == "__main__":
    bot.infinity_polling()
