# main.py
import telebot
import os
from database import init_db, add_reservation, get_user_reservations

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

# In-memory state storage (for simplicity — use Redis or DB in production)
user_states = {}
user_data = {}

# List of Services
SERVICES = [
    "بافت موی بلند",
    "بافت موی کوتاه",
    "مشاوره رایگان"
]

# Available time slots (you can make this dynamic based on date)
TIME_SLOTS = [
    "10:00 - 12:00",
    "14:00 - 16:00",
    "17:00 - 19:00"
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
        bot.send_message(message.chat.id, "سلام به ربات بافت مو بیجاری خوش آمدید! 🌿\nلطفاً یکی از گزینه‌ها رو انتخاب کنید:\n/book - رزرو نوبت\n/portfolio - نمونه کارها")
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
    bot.send_message(message.chat.id, "لطفاً سرویس مورد نظرتون رو انتخاب کنید:", reply_markup=markup)

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == STATE_ASKING_SERVICE)
def ask_date(message):
    user_id = message.from_user.id
    service = message.text
    if service not in SERVICES:
        bot.send_message(message.chat.id, "لطفاً یکی از گزینه‌های داده شده رو انتخاب کنید.")
        return

    user_data[user_id] = {'service': service}
    user_states[user_id] = STATE_ASKING_DATE
    bot.send_message(message.chat.id, "تاریخ دلخواهتون رو به فرمت YYYY-MM-DD وارد کنید (مثال: 2025-09-15):")

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == STATE_ASKING_DATE)
def ask_time(message):
    user_id = message.from_user.id
    date = message.text.strip()

    # Simple date validation (you can improve this)
    if len(date) != 10 or date[4] != '-' or date[7] != '-':
        bot.send_message(message.chat.id, "فرمت تاریخ اشتباهه. لطفاً به فرمت YYYY-MM-DD وارد کنید.")
        return

    user_data[user_id]['date'] = date
    user_states[user_id] = STATE_ASKING_TIME

    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    for slot in TIME_SLOTS:
        markup.add(slot)
    bot.send_message(message.chat.id, "ساعت دلخواهتون رو انتخاب کنید:", reply_markup=markup)

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == STATE_ASKING_TIME)
def ask_name_phone(message):
    user_id = message.from_user.id
    time_slot = message.text
    if time_slot not in TIME_SLOTS:
        bot.send_message(message.chat.id, "لطفاً یکی از بازه‌های زمانی داده شده رو انتخاب کنید.")
        return

    user_data[user_id]['time_slot'] = time_slot
    user_states[user_id] = STATE_ASKING_NAME_PHONE
    bot.send_message(message.chat.id, "لطفاً اسم و شماره تماس خودتون رو به این صورت وارد کنید:\nمثال: نرگس - 09123456789\n(لطفاً دقیقاً با این فرمت)")

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == STATE_ASKING_NAME_PHONE)
def finalize_booking(message):
    user_id = message.from_user.id
    try:
        name, phone = message.text.split(' - ')
    except ValueError:
        bot.send_message(message.chat.id, "فرمت اشتباهه! لطفاً مثل مثال وارد کنید: نرگس - 09123456789")
        return

    # Get data from user_data
    service = user_data[user_id]['service']
    date = user_data[user_id]['date']
    time_slot = user_data[user_id]['time_slot']

    # Save to database
    add_reservation(user_id, name, phone, service, date, time_slot)

    # Send confirmation
    confirmation_msg = f"""
✅ رزرو شما با موفقیت ثبت شد!

📅 تاریخ: {date}
⏰ ساعت: {time_slot}
💇‍♀️ سرویس: {service}
👤 نام: {name}
📞 شماره تماس: {phone}
📍 آدرس: خیابان اصلی، کوچه فلان، سالن بیجاری
📞 برای لغو یا تغییر نوبت، حداقل ۲۴ ساعت قبل تماس بگیرید.
    """
    bot.send_message(message.chat.id, confirmation_msg)

    # Reset user state
    user_states[user_id] = STATE_NONE
    del user_data[user_id]

    # Optional: Send notification to admin (you)
    # bot.send_message(YOUR_ADMIN_CHAT_ID, f"New reservation: {name} - {phone} - {service} on {date} at {time_slot}")

# فقط برای پیدا کردن ID کانال/گروه — بعد از پیدا کردن ID می‌تونید پاکش کنید
@bot.message_handler(commands=['getid'])
def get_chat_id(message):
    bot.reply_to(message, f"Chat ID: {message.chat.id}")

# Handle /portfolio command (placeholder for now)
@bot.message_handler(commands=['portfolio'])
def show_portfolio(message):
    user_id = message.from_user.id
    if not is_user_member(user_id):
        bot.send_message(message.chat.id, "لطفاً اول عضو کانال ما بشید.")
        return
    bot.send_message(message.chat.id, "در حال حاضر نمونه کارها در حال بارگذاری هستند. به زودی اضافه می‌شن!")

bot.polling()
