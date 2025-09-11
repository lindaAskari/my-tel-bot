import telebot
import os
# API_TOKEN = os.getenv('API_TOKEN')
API_TOKEN = os.getenv('API_TOKEN')

bot = telebot.TeleBot(token=API_TOKEN)

# جایگزین کنید با آیدی واقعی کانال بعد از اضافه کردن ربات به کانال
CHANNEL_ID = -1003053257734  # مثال: -1001987654321

def is_user_member(user_id):
    try:
        member = bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        if member.status in ['member', 'administrator', 'creator']:
            return True
    except Exception as e:
        print(f'Error checking membership: {e}')
    return False

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    if is_user_member(user_id):
        bot.send_message(message.chat.id, "Welcome... You are allowed to use the bot.")
    else:
        bot.send_message(message.chat.id, "You have to join the channel to use the bot.")

@bot.message_handler(commands=['help'])
def send_help(message):
    user_id = message.from_user.id
    if is_user_member(user_id):
        bot.send_message(message.chat.id, "This is the help message of the bot.")
    else:
        bot.send_message(message.chat.id, "You have to join the channel to use the bot.")

# فقط برای پیدا کردن ID کانال/گروه — بعد از پیدا کردن ID می‌تونید پاکش کنید
@bot.message_handler(commands=['getid'])
def get_chat_id(message):
    bot.reply_to(message, f"Chat ID: {message.chat.id}")

bot.polling()
