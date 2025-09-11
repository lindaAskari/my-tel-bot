# main.py
import telebot
import os
import time
import jdatetime
from database import init_db, add_reservation, get_user_reservations, add_portfolio_item, get_all_categories, get_portfolio_by_category

# Initialize Database
init_db()

# دریافت توکن از متغیر محیطی
API_TOKEN = os.getenv('API_TOKEN')
bot = telebot.TeleBot(token=API_TOKEN)

# تنظیمات کانال و ادمین
CHANNEL_ID = -1003053257734  # جایگزین کنید با آیدی واقعی کانال
ADMIN_CHAT_ID = 6020631201    # ✅ جایگزین کنید با آیدی عددی بهار بیجاری (از دستور /getid پیدا کنید)

# Define States
STATE_NONE = 0
STATE_ASKING_SERVICE = 1
STATE_ASKING_DATE = 2
STATE_ASKING_TIME = 3
STATE_ASKING_NAME = 4
STATE_ASKING_PHONE = 5
STATE_WAITING_FOR_CATEGORY = 'WAITING_FOR_CATEGORY'  # برای پورتفولیو
STATE_ADDING_PHOTO_CATEGORY = 'ADDING_PHOTO_CATEGORY'
STATE_ADDING_PHOTO_FILE = 'ADDING_PHOTO_FILE'

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

# Portfolio Categories
PORTFOLIO_CATEGORIES = [
    "بافت هلندی",
    "بافت خورشیدی",
    "بافت کراس",
    "بافت افریقایی",
    "بافت مرواریدی",
    "بافت تلی",
    "بافت کویین",
    "بافت تیغ ماهی"
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
    bot.send_message(message.chat.id, "لطفاً سرویس مورد نظرتون رو انتخاب کنید:", reply_markup=markup)

# مرحله ۱: دریافت سرویس
@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == STATE_ASKING_SERVICE)
def ask_date(message):
    user_id = message.from_user.id
    service = message.text
    if service not in SERVICES:
        bot.send_message(message.chat.id, "لطفاً یکی از گزینه‌های داده شده رو انتخاب کنید.")
        return

    user_data[user_id] = {'service': service}
    user_states[user_id] = STATE_ASKING_DATE
    bot.send_message(message.chat.id, "تاریخ دلخواهتون رو به فرمت YYYY-MM-DD وارد کنید (مثال: 1404-06-25):")

# مرحله ۲: دریافت تاریخ (شمسی)
@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == STATE_ASKING_DATE)
def ask_time_slot(message):
    user_id = message.from_user.id
    date_str = message.text.strip()

    try:
        year, month, day = map(int, date_str.split('-'))
        jdatetime.date(year, month, day)
    except (ValueError, IndexError):
        bot.send_message(message.chat.id, "فرمت تاریخ اشتباهه. لطفاً به فرمت YYYY-MM-DD وارد کنید (مثال: 1404-06-25).")
        return

    user_data[user_id]['date'] = date_str
    user_states[user_id] = STATE_ASKING_TIME

    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    for slot in TIME_SLOTS:
        markup.add(slot)
    bot.send_message(message.chat.id, "ساعت دلخواهتون رو انتخاب کنید:", reply_markup=markup)

# مرحله ۳: دریافت ساعت → بعدش می‌ریم سراغ اسم
@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == STATE_ASKING_TIME)
def ask_name(message):
    user_id = message.from_user.id
    time_slot = message.text
    if time_slot not in TIME_SLOTS:
        bot.send_message(message.chat.id, "لطفاً یکی از بازه‌های زمانی داده شده رو انتخاب کنید.")
        return

    user_data[user_id]['time_slot'] = time_slot
    user_states[user_id] = STATE_ASKING_NAME
    bot.send_message(message.chat.id, "لطفاً *اسم و فامیل* خودتون رو وارد کنید:")

# مرحله ۴: دریافت اسم → بعدش می‌ریم سراغ شماره
@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == STATE_ASKING_NAME)
def ask_phone(message):
    user_id = message.from_user.id
    name = message.text.strip()
    if not name:
        bot.send_message(message.chat.id, "لطفاً یک اسم معتبر وارد کنید.")
        return

    user_data[user_id]['name'] = name
    user_states[user_id] = STATE_ASKING_PHONE
    bot.send_message(message.chat.id, "حالا لطفاً *شماره تلفن* خودتون رو وارد کنید (مثال: 09123456789):")

# مرحله ۵: دریافت شماره و ثبت نهایی
@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == STATE_ASKING_PHONE)
def finalize_booking(message):
    user_id = message.from_user.id
    phone = message.text.strip()

    # اعتبارسنجی ساده شماره موبایل
    if not phone.startswith('09') or len(phone) != 11 or not phone.isdigit():
        bot.send_message(message.chat.id, "شماره تلفن اشتباهه! لطفاً یه شماره معتبر وارد کنید (مثال: 09123456789).")
        return

    service = user_data[user_id]['service']
    date = user_data[user_id]['date']
    time_slot = user_data[user_id]['time_slot']
    name = user_data[user_id]['name']

    # Save to database
    add_reservation(user_id, name, phone, service, date, time_slot)

    # Send confirmation
    confirmation_msg = f"""
✅ رزرو شما با موفقیت ثبت شد!

📅 تاریخ: {date} (شمسی)
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
    if user_id in user_data:
        del user_data[user_id]

# ============================
# 🖼️ بخش گالری نمونه کارها
# ============================

@bot.message_handler(commands=['portfolio'])
def show_portfolio_categories(message):
    user_id = message.from_user.id
    if not is_user_member(user_id):
        bot.send_message(message.chat.id, "لطفاً اول عضو کانال ما بشید.")
        return

    # دریافت لیست دسته‌بندی‌ها از دیتابیس
    categories = get_all_categories()

    # اگر هیچ دسته‌بندی‌ای وجود نداشت، از لیست پیش‌فرض استفاده کن
    if not categories:
        categories = PORTFOLIO_CATEGORIES

    if not categories:
        bot.send_message(message.chat.id, "متاسفانه هنوز نمونه کاری اضافه نشده است.")
        return

    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    for cat in categories:
        markup.add(cat)

    bot.send_message(message.chat.id, "کدوم دسته از کارهامو می‌خوای ببینی؟", reply_markup=markup)
    user_states[user_id] = STATE_WAITING_FOR_CATEGORY

# هندلر برای زمانی که کاربر یک دسته‌بندی رو انتخاب می‌کنه
@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == STATE_WAITING_FOR_CATEGORY)
def send_portfolio_items(message):
    user_id = message.from_user.id
    category = message.text

    # دریافت تمام آیتم‌های این دسته‌بندی
    items = get_portfolio_by_category(category)

    if not items:
        bot.send_message(message.chat.id, f"متاسفانه هنوز نمونه کاری برای '{category}' اضافه نشده است.")
    else:
        bot.send_message(message.chat.id, f"نمونه کارهای '{category}':")
        for image_path, caption in items:
            try:
                with open(image_path, 'rb') as photo:
                    bot.send_photo(message.chat.id, photo, caption=caption or category)
            except Exception as e:
                print(f"Error sending photo {image_path}: {e}")
                bot.send_message(message.chat.id, f"⚠️ خطایی در نمایش یکی از عکس‌ها رخ داد.")

    # بازگشت به حالت عادی
    user_states[user_id] = STATE_NONE

# ============================
# 🛠️ بخش ادمین — آپلود نمونه کار
# ============================

@bot.message_handler(commands=['add_photo'])
def start_adding_photo(message):
    # فقط ادمین می‌تونه ازش استفاده کنه
    if message.from_user.id != ADMIN_CHAT_ID:
        bot.send_message(message.chat.id, "شما مجاز به استفاده از این دستور نیستید.")
        return

    bot.send_message(message.chat.id, "لطفاً دسته‌بندی مورد نظر رو انتخاب کنید:", reply_markup=get_category_markup())
    user_states[ADMIN_CHAT_ID] = STATE_ADDING_PHOTO_CATEGORY

def get_category_markup():
    categories = get_all_categories()
    if not categories:
        categories = PORTFOLIO_CATEGORIES
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    for cat in categories:
        markup.add(cat)
    return markup

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == STATE_ADDING_PHOTO_CATEGORY)
def ask_for_photo(message):
    if message.from_user.id != ADMIN_CHAT_ID:
        return

    category = message.text
    user_data[ADMIN_CHAT_ID] = {'category': category}
    bot.send_message(message.chat.id, "حالا لطفاً عکس نمونه کار رو بفرستید (ترجیحاً با کیفیت خوب).")
    user_states[ADMIN_CHAT_ID] = STATE_ADDING_PHOTO_FILE

@bot.message_handler(content_types=['photo'], func=lambda message: user_states.get(message.from_user.id) == STATE_ADDING_PHOTO_FILE)
def receive_photo(message):
    if message.from_user.id != ADMIN_CHAT_ID:
        return

    # دریافت آخرین عکس با بالاترین رزولوشن
    file_id = message.photo[-1].file_id
    file_info = bot.get_file(file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    # ذخیره عکس در پوشه static/portfolio
    category = user_data[ADMIN_CHAT_ID]['category']
    safe_category_name = "".join(c if c.isalnum() or c in " _-" else "_" for c in category)
    filename = f"{safe_category_name}_{int(time.time())}.jpg"
    filepath = f"static/portfolio/{filename}"

    # ایجاد پوشه اگر وجود نداشت
    os.makedirs("static/portfolio", exist_ok=True)

    with open(filepath, 'wb') as new_file:
        new_file.write(downloaded_file)

    # ذخیره در دیتابیس
    caption = message.caption or f"نمونه کار {category}"
    add_portfolio_item(category, filepath, caption)

    bot.send_message(message.chat.id, f"✅ عکس با موفقیت در دسته‌بندی '{category}' اضافه شد!")
    user_states[ADMIN_CHAT_ID] = STATE_NONE
    if ADMIN_CHAT_ID in user_data:
        del user_data[ADMIN_CHAT_ID]

# فقط برای پیدا کردن ID کانال/گروه — بعد از پیدا کردن ID می‌تونید پاکش کنید
@bot.message_handler(commands=['getid'])
def get_chat_id(message):
    bot.reply_to(message, f"Chat ID: {message.chat.id}")

bot.polling()
