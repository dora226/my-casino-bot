import telebot
import os
import random
from flask import Flask
from threading import Thread

# --- ПОЛНАЯ ЗАЩИТА ОТ ОШИБОК RENDER (PORT SCAN TIMEOUT) ---
app = Flask('')

@app.route('/')
def home():
    return "Casino is running 24/7!"

def run():
    # Render автоматически подставит нужный порт
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run, daemon=True)
    t.start()

# Запускаем веб-сервер перед стартом бота
keep_alive()

# --- НАСТРОЙКИ БОТА ---
# Твой новый токен, который ты скинул
TOKEN = "8412093219:AAGmPVtgX1wA133UGsya3UnDf_B5SPphBkM"
bot = telebot.TeleBot(TOKEN)
ADMIN_ID = 7232292366 

users = {} 
admin_lucky_mode = True 

def get_bal(uid):
    if uid not in users: users[uid] = 1000
    return users[uid]

# --- КОМАНДЫ ---

@bot.message_handler(commands=['id'])
def get_user_id(message):
    if message.reply_to_message:
        target_id = message.reply_to_message.from_user.id
        bot.reply_to(message, f"🆔 ID пользователя: `{target_id}`", parse_mode="Markdown")
    else:
        bot.reply_to(message, f"🆔 Твой ID: `{message.from_user.id}`", parse_mode="Markdown")

@bot.message_handler(commands=['lucky'])
def toggle_lucky(message):
    global admin_lucky_mode
    if message.from_user.id != ADMIN_ID: return
    admin_lucky_mode = not admin_lucky_mode
    status = "✅ ВКЛЮЧЕН" if admin_lucky_mode else "❌ ВЫКЛЮЧЕН"
    bot.reply_to(message, f"🎰 Режим повышенного шанса: **{status}**", parse_mode="Markdown")

@bot.message_handler(commands=['start', 'profile'])
def profile(message):
    uid = message.from_user.id
    bal = get_bal(uid)
    status = "👑 Владелец" if uid == ADMIN_ID else "👤 Игрок"
    lucky = "\n🍀 Шансы: **ПОВЫШЕНЫ**" if (uid == ADMIN_ID and admin_lucky_mode) else ""
    text = (f"🎰 **КАЗИНО**\n\n🔹 Статус: {status}{lucky}\n💰 Баланс: {bal}$\n\n"
            f"🎮 `/slots [ставка]`\n🎡 `/roulette [ставка] [red/black]`")
    bot.reply_to(message, text, parse_mode="Markdown")

@bot.message_handler(commands=['slots'])
def slots(message):
    uid = message.from_user.id
    try:
        bet = int(message.text.split()[1])
    except: return bot.reply_to(message, "Использование: `/slots 100`", parse_mode="Markdown")
    if bet > get_bal(uid) or bet <= 0: return bot.reply_to(message, "❌ Недостаточно средств!")

    # 50% шанс для тебя, 15% для остальных
    threshold = 50 if (uid == ADMIN_ID and admin_lucky_mode) else 15
    emojis = ["💎", "🎰", "🍒", "7️⃣"]
    
    if random.randint(1, 100) <= threshold:
        res = [random.choice(emojis)] * 3
        users[uid] += bet * 3
        msg = f"🔥 ПОБЕДА! +{bet * 3}$"
    else:
        res = [random.choice(emojis) for _ in range(3)]
        users[uid] -= bet
        msg = f"📉 Проигрыш. -{bet}$"
    bot.send_message(message.chat.id, f"| {' | '.join(res)} |\n\n{msg}\nБаланс: {users[uid]}$")

@bot.message_handler(commands=['give'])
def give_money(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        _, target, amount = message.text.split()
        target, amount = int(target), int(amount)
        users[target] = users.get(target, 0) + amount
        bot.reply_to(message, f"✅ Выдано {amount}$ игроку `{target}`", parse_mode="Markdown")
    except: bot.reply_to(message, "Ошибка! `/give [id] [сумма]`")

# Бесконечный цикл без вылетов
if __name__ == "__main__":
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
