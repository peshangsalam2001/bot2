import telebot
from telebot import types

API_TOKEN = '7007340673:AAEhp1W1PhoUq_rOcssQVDIvq0OZVEXHARM'
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

# فەرمی سەرەتا
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    user_coins.setdefault(user_id, 0)

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
    bot.send_photo(user_id, photo_url, caption=caption, reply_markup=markup)

# handle callback buttons
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    user_id = call.from_user.id
    first_name = call.from_user.first_name

    if user_id not in user_coins:
        user_coins[user_id] = 0

    if call.data == 'my_coins':
        user_steps[user_id] = 'main_menu'
        coins = user_coins.get(user_id, 0)
        text = f"""بەڕێز {first_name}، ئەم کۆینە بۆ مەبەستی کڕینی کۆرسەکان بەکاردێت.

تۆ ئێستا {coins} کۆینت هەیە.
دەتوانیت لەڕێگەی لینکی بانگهێشتنامە یاخود کڕینی کۆرسەکان بتوانی کۆینی زۆرتر کۆبکەیتەوە.
"""
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("گەڕانەوە", callback_data='back'))
        bot.send_message(call.message.chat.id, text, reply_markup=markup)

    elif call.data == 'invite_link':
        user_steps[user_id] = 'main_menu'
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("کۆپی کردنی لینک", url=invite_link))
        markup.add(types.InlineKeyboardButton("گەڕانەوە", callback_data='back'))
        bot.send_message(call.message.chat.id, "ئەمە لینکی بانگهێشتنامەکەتە:", reply_markup=markup)

    elif call.data == 'courses':
        user_steps[user_id] = 'courses'
        markup = types.InlineKeyboardMarkup()
        for course, price in courses_data.items():
            markup.add(types.InlineKeyboardButton(f"{course} ({price} کۆین)", callback_data=f"buy_{course}"))
        markup.add(types.InlineKeyboardButton("گەڕانەوە", callback_data='back'))
        bot.send_message(call.message.chat.id, "کۆرسە بەردەستەکان:", reply_markup=markup)

    elif call.data.startswith("buy_"):
        course_name = call.data.replace("buy_", "")
        price = courses_data.get(course_name, 0)
        if user_coins[user_id] >= price:
            user_coins[user_id] -= price
            bot.send_message(call.message.chat.id, f"پیرۆزە! کۆرسی '{course_name}' بەسەرکەوتوویی کڕدرایەوە.")
        else:
            bot.send_message(call.message.chat.id, "ببوورە، تۆ بڕی پێویست لە کۆینت نیە بۆ کڕینی ئەم کۆرسە.")

        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("گەڕانەوە", callback_data='back'))
        bot.send_message(call.message.chat.id, "دەست خۆشبێ!", reply_markup=markup)

    elif call.data == 'all_bots':
        user_steps[user_id] = 'main_menu'
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("@PeshangTestBot", url="https://t.me/PeshangTestBot"))
        markup.add(types.InlineKeyboardButton("گەڕانەوە", callback_data='back'))
        bot.send_message(call.message.chat.id, "ئەمە بۆتە تایبەتیەکانت:", reply_markup=markup)

    elif call.data == 'back':
        show_main_menu(call.message.chat.id, first_name)

def show_main_menu(chat_id, first_name):
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
    bot.send_photo(chat_id, photo_url, caption=caption, reply_markup=markup)

# Start bot
bot.polling()
