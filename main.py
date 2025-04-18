import telebot
from telebot import types

API_TOKEN = '8072279299:AAF-iMur2T62-LDnXXsQVGSg16Lqc1f1UXA'
bot = telebot.TeleBot(API_TOKEN)

# داتاکان
user_coins = {}
user_steps = {}

# زانیاری کۆرسەکان
courses_data = {
    'کۆرسی مایکرۆسۆفت ئێکسڵ': 20,
    'کۆرسی زمانی پایسۆن': 15,
    'کۆرسی مایکرۆسۆفت ئەکسس': 10
}

# لینکی بانگهێشت
invite_link = 'https://t.me/Kurd2Bot_Bot?start=ref'

# بەکارهێنانەوەی نامەی سەرەتا
def send_welcome_message(chat_id, first_name, message_id=None):
    photo_url = 'https://i.imgur.com/CwdrpWr.jpeg'
    caption = f"""سڵاو بەڕێز {first_name}، بەخێربێیت بۆ بۆتی ئەکادیمیای پێشەنگ.
ئەم بۆتە تایبەتە بە کۆمەڵێک خزمەتگوزاری و زانیاری، هەر یەکە لە کڕینی کۆرس، زانینی کۆینەکانت، زانیاری تەکنەلۆجی و زۆر شتی تر.

بۆ هەر یەکێک لەو تایبەتمەندیانە پەنجە بە دوگمەی مەبەست بنێ:
"""
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("کۆینەکانم", callback_data='my_coins'),
        types.InlineKeyboardButton("لینکی بانگهێشتنامە", callback_data='invite_link'),
        types.InlineKeyboardButton("کۆرسەکان", callback_data='courses'),
        types.InlineKeyboardButton("هەموو بۆتەکانم", callback_data='all_bots')
    )

    if message_id:
        bot.edit_message_media(media=types.InputMediaPhoto(media=photo_url, caption=caption), chat_id=chat_id, message_id=message_id, reply_markup=markup)
    else:
        bot.send_photo(chat_id, photo_url, caption=caption, reply_markup=markup)

# فرمانی start
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    user_coins.setdefault(user_id, 0)
    user_steps[user_id] = 'main_menu'
    send_welcome_message(user_id, first_name)

# دوگمەکان
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    msg_id = call.message.message_id
    first_name = call.from_user.first_name
    user_coins.setdefault(user_id, 0)

    if call.data == 'my_coins':
        text = f"""بەڕێز {first_name}، ئەم کۆینە بۆ مەبەستی کڕینی کۆرسەکان بەکاردێت.

تۆ ئێستا {user_coins[user_id]} کۆینت هەیە.
دەتوانیت لەڕێگەی لینکی بانگهێشتنامە یان کڕینی کۆرسەکان، کۆینی زۆرتر کۆبکەیتەوە."""
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("گەڕانەوە", callback_data='back'))
        bot.edit_message_caption(chat_id=chat_id, message_id=msg_id, caption=text, reply_markup=markup)

    elif call.data == 'invite_link':
        text = f"""ئەمە لینکی بانگهێشتنامەکەتە:

{invite_link}"""
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("گەڕانەوە", callback_data='back'))
        bot.edit_message_caption(chat_id=chat_id, message_id=msg_id, caption=text, reply_markup=markup)

    elif call.data == 'courses':
        markup = types.InlineKeyboardMarkup()
        for course, price in courses_data.items():
            markup.add(types.InlineKeyboardButton(f"{course} ({price} کۆین)", callback_data=f"buy_{course}"))
        markup.add(types.InlineKeyboardButton("گەڕانەوە", callback_data='back'))
        bot.edit_message_caption(chat_id=chat_id, message_id=msg_id, caption="کۆرسە بەردەستەکان:", reply_markup=markup)
        user_steps[user_id] = 'courses'

    elif call.data.startswith("buy_"):
        course_name = call.data.replace("buy_", "")
        price = courses_data.get(course_name, 0)
        if user_coins[user_id] >= price:
            user_coins[user_id] -= price
            text = f"پیرۆزە! کۆرسی '{course_name}' بەسەرکەوتوویی کڕدرایەوە."
        else:
            text = "ببوورە، تۆ بڕی پێویست لە کۆینت نیە بۆ کڕینی ئەم کۆرسە."
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("گەڕانەوە", callback_data='back'))
        bot.edit_message_caption(chat_id=chat_id, message_id=msg_id, caption=text, reply_markup=markup)

    elif call.data == 'all_bots':
        text = "ئەمە بۆتە تایبەتیەکانت:\n@PeshangTestBot"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("گەڕانەوە", callback_data='back'))
        bot.edit_message_caption(chat_id=chat_id, message_id=msg_id, caption=text, reply_markup=markup)

    elif call.data == 'back':
        send_welcome_message(chat_id, first_name, message_id=msg_id)
        user_steps[user_id] = 'main_menu'

# ڕاگرتنی بۆتەکە
bot.polling()