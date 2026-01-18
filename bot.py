import telebot
import os
import random
from flask import Flask
from threading import Thread

# --- СЕРВЕР ДЛЯ RENDER ---
app = Flask('')
@app.route('/')
def home(): return "Бот Казино Активен!"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

# --- НАСТРОЙКИ ---
TOKEN = "8412093219:AAGmPVtgX1wA133UGsya3UnDf_B5SPphBkM"
bot = telebot.TeleBot(TOKEN)
ADMIN_ID = 7232292366 

users = {} 
lucky_mode = True 

def get_bal(uid):
    if uid not in users: users[uid] = 1000
    return users[uid]

# --- НОВАЯ ФУНКЦИЯ: +10000ккк РЕПЛАЕМ ---
@bot.message_handler(func=lambda m: m.reply_to_message and m.text and "+10000ккк" in m.text.lower())
def add_money_reply(m):
    if m.from_user.id != ADMIN_ID: return
    
    target_id = m.reply_to_message.from_user.id
    amount = 10000000000  # 10ккк
    
    users[target_id] = get_bal(target_id) + amount
    bot.reply_to(m, f"✅ Босс, начислил игроку {amount}$! Теперь у него {users[target_id]}$")

# --- КОМАНДА /ID РЕПЛАЕМ ---
@bot.message_handler(commands=['id'])
def get_id(m):
    uid = m.reply_to_message.from_user.id if m.reply_to_message else m.from_user.id
    bot.reply_to(m, f"🆔 ID: `{uid}`", parse_mode="Markdown")

# --- ПЕРЕКЛЮЧАТЕЛЬ ШАНСОВ ---
@bot.message_handler(commands=['lucky'])
def toggle(m):
    global lucky_mode
    if m.from_user.id != ADMIN_ID: return
    lucky_mode = not lucky_mode
    bot.reply_to(m, f"🍀 Твой повышенный шанс: {'✅ ВКЛ (50%)' if lucky_mode else '❌ ВЫКЛ (15%)'}")

@bot.message_handler(commands=['start', 'profile'])
def profile(m):
    uid = m.from_user.id
    bal = get_bal(uid)
    text = f"🎰 **КАЗИНО**\n💰 Баланс: {bal}$\n\n/slots [ставка]"
    if uid == ADMIN_ID:
        text += f"\n👑 Режим админа: {'Удача 50%' if lucky_mode else 'Обычный'}"
    bot.reply_to(m, text, parse_mode="Markdown")

@bot.message_handler(commands=['slots'])
def slots(m):
    uid = m.from_user.id
    try:
        bet = int(m.text.split()[1])
        bal = get_bal(uid)
        if bet > bal or bet <= 0: return bot.reply_to(m, "❌ Недостаточно средств!")
    except: return bot.reply_to(m, "Используй: /slots 100")

    chance = 50 if (uid == ADMIN_ID and lucky_mode) else 15
    win = random.randint(1, 100) <= chance
    
    if win: 
        users[uid] = bal + (bet * 2)
        res = "🎰 | 🎰 | 🎰\n\n🔥 ВЫИГРАЛ!"
    else: 
        users[uid] = bal - bet
        res = "🍒 | 🍋 | 💎\n\n📉 ПРОИГРАЛ"
    
    bot.reply_to(m, f"{res}\nБаланс: {users[uid]}$")

if __name__ == "__main__":
    Thread(target=run).start()
    bot.infinity_polling()
