# main.py
import telebot
import os
from database import init_db, add_reservation, get_user_reservations
import jdatetime

# Initialize Database
init_db()

API_TOKEN = os.getenv('API_TOKEN')
bot = telebot.TeleBot(token=API_TOKEN)

# جایگزین کنید با آیدی واقعی کانال بعد از اضافه کردن ربات به کانال
CHANNEL_ID = -1003053257734

# Define States
STATE_NONE = 0
STATE_ASKING_SERVICE = 1
STATE_ASKING_DATE = 2
STATE_ASKING_TIME = 3
STATE_ASKING_NAME_PHONE = 4

# In-memory state storage
user_states = {}
user_data = {}

# List of Services
SERVICES = [
    "بافت مو",
    "کوتاهی مو",
    "مشاوره رایگان"
]

# Available time slots
TIME_SLOTS = [
    "10:00 - 12:00",
    "12:00 - 14:00",
    "14:00 - 16:00",
    "16:00 - 18:00",
    "18:00 - 20:00",
    "20:00 - 22:00",
]

def is_user_member(user_id):
    try:
        member = bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        print(f'Error checking membership: {e}')
        return False

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    if is_user_member(user_id):
        bot.send_message(message.chat.id, "سلام به ربات بافت مو بیجاری خوش آمدید! 💜\nلطفاً یکی از گزینه‌ها رو انتخاب کنید:\n/book - رزرو نوبت\n/portfolio - نمونه کارها")
    else:
        bot.send_message(message.chat.id, "لطفاً اول عضو کانال ما بشید تا بتونید از ربات استفاده کنید.")

@bot.message_handler(commands=['book'])
def start_booking(message):
    user_id = message.from_user.id
    if not is_user_member(user_id):
        bot.send_message(message.chat.id, "لطفاً اول عضو کانال ما بشید.")
        return

    user_states[user_id] = STATE_ASKING_SERVICE
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    for service in SERVICES:
        markup.add(service)
    bot.send_message(message.chat.id, "ل
