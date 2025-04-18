import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# توکن و IDی خاوەنی بۆت
BOT_TOKEN = '8072279299:AAF-iMur2T62-LDnXXsQVGSg16Lqc1f1UXA'
OWNER_ID = 1908245207  # گۆڕە بە IDی تەلەگرامەکەت

bot = telebot.TeleBot(BOT_TOKEN)

# هەژمارەکانی بەکارهێنەران
users = {}  # Format: user_id: {"coins": int, "invited": set()}
required_coins = 3

# لیستی کۆرسەکان
courses = {
    "Excel Basic": "https://example.com/excel-basic",
    "Word Advanced": "https://example.com/word-advanced",
    "PowerPoint Design": "https://example.com/powerpoint-design"
}

# Command: /start
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    if user_id not in users:
        users[user_id] = {"coins": 0, "invited": set()}
    bot.send_message(message.chat.id,
        f"بەخێربێیت بۆ بۆتی فرۆشتنی کۆرسەکان!\n"
        f"بۆ بەدەست هێنانی کۆرس، پێویستە {required_coins} کۆینت هەبێت.\n"
        f"هەرکاتێک هاوڕێکت هێنایە بۆ ناو بۆتەکە، ١ کۆین دەدەیت.\n"
        f"بۆ بینینی لینک: /invite")

# Command: /invite
@bot.message_handler(commands=['invite'])
def invite(message):
    user_id = message.from_user.id
    invite_link = f"https://t.me/YOUR_BOT_USERNAME?start={user_id}"
    bot.send_message(message.chat.id,
                     f"هاوڕێیەکت بەڵێ بۆ ئەم لینکە کلیک بکات:\n{invite_link}")

# Command: /coins
@bot.message_handler(commands=['coins'])
def coins(message):
    user_id = message.from_user.id
    coins = users.get(user_id, {"coins": 0})["coins"]
    bot.send_message(message.chat.id, f"تۆ {coins} کۆینت هەیە.")

# Command: /getcourse — تەنیا بۆ خاوەن
@bot.message_handler(commands=['getcourse'])
def get_course_menu(message):
    user_id = message.from_user.id

    if user_id != OWNER_ID:
        bot.send_message(message.chat.id, "ببورە، تەنیا خاوەنی بۆت دەتوانێت کۆرسەکان ببینێ.")
        return

    user_data = users.get(user_id, {"coins": 0})
    if user_data["coins"] < required_coins:
        bot.send_message(message.chat.id,
                         f"پێویستە {required_coins} کۆینت هەبێت.\n"
                         f"ئێستا کۆینەکانت: {user_data['coins']}")
        return

    markup = InlineKeyboardMarkup()
    for name in courses:
        markup.add(InlineKeyboardButton(text=name, callback_data=f"course:{name}"))
    bot.send_message(message.chat.id, "تکایە کۆرسێک هەڵبژێرە:", reply_markup=markup)

# Callback: بۆ ناردنی لینکەکە
@bot.callback_query_handler(func=lambda call: call.data.startswith("course:"))
def send_course_link(call):
    course_name = call.data.split(":")[1]
    user_id = call.from_user.id
    user_data = users.get(user_id, {"coins": 0})
    
    if user_id != OWNER_ID:
        bot.send_message(call.message.chat.id, "تەنیا خاوەنی بۆت دەتوانێت لینکەکان ببینێ.")
        return

    if user_data["coins"] >= required_coins:
        link = courses.get(course_name)
        bot.send_message(call.message.chat.id,
                         f"ئەمە لینکی کۆرسی {course_name} ـە:\n{link}")
    else:
        bot.send_message(call.message.chat.id,
                         f"کۆینی پێویستت نییە بۆ گرتنی کۆرسەکە.")

# Referral handler
@bot.message_handler(func=lambda message: message.text.startswith("/start ") and len(message.text.split()) == 2)
def handle_referral(message):
    user_id = message.from_user.id
    referrer_id = int(message.text.split()[1])
    if user_id == referrer_id:
        bot.send_message(message.chat.id, "ناتوانیت خۆت ڕیفەر بکەیت!")
        return

    if user_id not in users:
        users[user_id] = {"coins": 0, "invited": set()}

    if referrer_id in users and user_id not in users[referrer_id]["invited"]:
        users[referrer_id]["coins"] += 1
        users[referrer_id]["invited"].add(user_id)
        bot.send_message(referrer_id, "کەسێکی نوێت هێنا! ١ کۆین زیاد کرایەوە.")

    bot.send_message(message.chat.id, "بەخێربێیت! لە ئێستا دەستی پێ بکە بە هەڵگرتنی کۆین!")

# Run the bot
print("Bot is running...")
bot.infinity_polling()