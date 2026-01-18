import telebot
import sqlite3
import random
import time
from datetime import datetime, timedelta

# --- КОНФИГУРАЦИЯ ---
TOKEN = "8412093219:AAGcC6jTvTOkpduhx5Sdgruo1u3K_ZY2Kgk"
OWNER_ID = 7232292366 

bot = telebot.TeleBot(TOKEN, parse_mode="Markdown")

# --- БАЗА ДАННЫХ ---
conn = sqlite3.connect("casino_galaxy.sqlite", check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS users 
               (id INTEGER PRIMARY KEY, username TEXT, money INTEGER DEFAULT 5000, 
                crystals INTEGER DEFAULT 0, games_count INTEGER DEFAULT 0, 
                luck_mode INTEGER DEFAULT 0, has_card INTEGER DEFAULT 0, 
                has_amulet INTEGER DEFAULT 0, has_ultra INTEGER DEFAULT 0,
                losses_count INTEGER DEFAULT 0, custom_rank TEXT, last_bonus TEXT)''')
conn.commit()

# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---
def get_user(user_id, username="Игрок"):
    cursor.execute("SELECT money, crystals, games_count, luck_mode, has_card, has_amulet, has_ultra, losses_count, custom_rank, last_bonus FROM users WHERE id = ?", (user_id,))
    res = cursor.fetchone()
    if not res:
        cursor.execute("INSERT INTO users (id, username) VALUES (?, ?)", (user_id, username))
        conn.commit()
        return (5000
