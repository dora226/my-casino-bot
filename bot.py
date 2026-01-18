import telebot, sqlite3, random, time
from datetime import datetime, timedelta

# --- НАСТРОЙКИ ---
TOKEN = "8412093219:AAHCL63Tq58_aYi5YgpVP5m-xOvDSma-V4M"
OWNER_ID = 7232292366 
bot = telebot.TeleBot(TOKEN, parse_mode="Markdown")

# --- БАЗА ДАННЫХ ---
conn = sqlite3.connect("casino_v10.sqlite", check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS users 
    (id INTEGER PRIMARY KEY, money INTEGER DEFAULT 5000, 
    crystals INTEGER DEFAULT 0, games_count INTEGER DEFAULT 0, 
    luck_mode INTEGER DEFAULT 0, has_card INTEGER DEFAULT 0, 
    has_amulet INTEGER DEFAULT 0, has_ultra INTEGER DEFAULT 0,
    losses_count INTEGER DEFAULT 0, custom_rank TEXT, last_bonus TEXT)''')
conn.commit()

def get_user(uid):
    cursor.execute("SELECT money, crystals, games_count, luck_mode, has_card, has_amulet, has_ultra, losses_count, custom_rank, last_bonus FROM users WHERE id = ?", (uid,))
    res = cursor.fetchone()
    if not res:
        cursor.execute("INSERT INTO users (id) VALUES (?)", (uid,))
        conn.commit()
        return (5000, 0, 0, 0, 0, 0, 0, 0, None, None)
    return res

def update_db(uid, **kwargs):
    for key, value in kwargs.items():
        if isinstance(value, str) or value is None:
            cursor.execute(f"UPDATE users SET {key} = ? WHERE id = ?", (value, uid))
        else:
            cursor.execute(f"UPDATE users SET {key} = {key} + ? WHERE id = ?", (value, uid))
    conn.commit()

# --- АДМИНКА (ВЫДАЧА РЕПЛАЕМ) ---
@bot.message_handler(func=lambda m: m.from_user.id == OWNER_ID and m.reply_to_message)
def admin_reply(m):
    t = m.text.lower()
    tid = m.reply_to_message.from_user.id
    if t.startswith("ранг "):
        update_db(tid, custom_rank=m.text[5:])
        bot.reply_to(m, "✅ Ранг изменен!")
    elif "+" in t or "-" in t:
        num = int(''.join(filter(str.isdigit, t.replace("к", "000"))))
        val = num if "+" in t else -num
        if "кри" in t: update_db(tid, crystals=val)
        else: update_db(tid, money=val)
        bot.reply_to(m, "✅ Выдано!")

# --- ОСНОВНЫЕ КОМАНДЫ ---
@bot.message_handler(func=lambda m: m.text == "👤 ПРОФИЛЬ")
def profile(m):
    mon, cry, gc, luck, card, am, ultra, loss, cust, _ = get_user(m.from_user.id)
    rank = cust if cust else ("💎 Миллионер" if mon >= 1000000 else "🌱 Новичок")
    bot.send_message(m.chat.id, f"👤 *Имя:* {m.from_user.first_name}\n🎖 *Ранг:* {rank}\n💰 *Баланс:* {mon:,}$\n💎 *Кристаллы:* {cry}")

@bot.message_handler(func=lambda m: m.text == "🛒 МАГАЗИН")
def shop(m):
    kb = telebot.types.InlineKeyboardMarkup()
    kb.add(telebot.types.InlineKeyboardButton("💎 Кристалл (5к$)", callback_data="buy_c"))
    bot.send_message(m.chat.id, "🛒 *МАГАЗИН*", reply_markup=kb)

@bot.callback_query_handler(func=lambda call: True)
def calls(call):
    u = call.from_user.id
    m, c, _, luck, _, _, _, _, _, _ = get_user(u)
    if call.data == "buy_c" and m >= 5000:
        update_db(u, money=-5000, crystals=1)
        bot.answer_callback_query(call.id, "💎 Куплено!")
    elif call.data == "toggle_luck" and u == OWNER_ID:
        update_db(u, luck_mode=(0 if luck else 1))
        bot.answer_callback_query(call.id, f"Удача: {'ВКЛ' if not luck else 'ВЫКЛ'}", show_alert=True)

@bot.message_handler(func=lambda m: m.text and m.text.lower().startswith(("сл", "бас")))
def games(m):
    args = m.text.lower().split()
    if len(args) < 2: return
    try: bet = int(args[1].replace("к", "000"))
    except: return
    mon, _, _, luck, _, _, _, _, _, _ = get_user(m.from_user.id)
    if mon < bet: return bot.reply_to(m, "❌ Нет денег!")
    update_db(m.from_user.id, money=-bet)
    res = bot.send_dice(m.chat.id, emoji="🎰" if "сл" in m.text.lower() else "🏀")
    time.sleep(4)
    if res.dice.value in [1, 22, 43, 64, 4, 5] or luck == 1:
        update_db(m.from_user.id, money=bet*2)
        bot.reply_to(m, "✅ ПОБЕДА!")
    else: bot.reply_to(m, "❌ ПРОИГРЫШ")

@bot.message_handler(commands=['start'])
def start(m):
    get_user(m.from_user.id)
    kb = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("🎰 ИГРАТЬ", "👤 ПРОФИЛЬ")
    kb.row("🛒 МАГАЗИН", "⚙️ АДМИНКА")
    bot.send_message(m.chat.id, "💎 Казино запущено!", reply_markup=kb)

@bot.message_handler(func=lambda m: m.text == "⚙️ АДМИНКА")
def admin(m):
    if m.from_user.id == OWNER_ID:
        kb = telebot.types.InlineKeyboardMarkup()
        kb.add(telebot.types.InlineKeyboardButton("🍀 УДАЧА", callback_data="toggle_luck"))
        bot.send_message(m.chat.id, "🛠 Админ-меню:", reply_markup=kb)

if __name__ == "__main__":
    bot.infinity_polling()
