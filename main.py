import telebot
from telebot import types

TOKEN = '8072279299:AAF-iMur2T62-LDnXXsQVGSg16Lqc1f1UXA'
BOT_USERNAME = 'PeshangTestBot'

bot = telebot.TeleBot(TOKEN)

user_coins = {}
invited_users = set()

# نرخەکانی کۆرسەکان
courses_data = {
    "Microsoft Excel": 20,
    "Python": 15,
    "Microsoft Access": 10
}

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    args = message.text.split()

    # دابینکردنی هەژماری نوێ
    if user_id not in user_coins:
        user_coins[user_id] = 0

    # بەکارهێنەری نوێ لە ڕێگەی بانگەوازەوە
    if len(args) > 1:
        inviter_id = args[1]
        if inviter_id != str(user_id):
            key = f"{inviter_id}_{user_id}"
            if key not in invited_users:
                invited_users.add(key)
                user_coins[int(inviter_id)] = user_coins.get(int(inviter_id), 0) + 1
                bot.send_message(int(inviter_id), f"کەسێک بە بانگەوازت هاتە ناو بۆتەکە. 1 کۆینت زیاد کرا.")

    # وێنە + نامەی سەرەتا
    photo_url = 'https://i.imgur.com/CwdrpWr.jpeg'  # وێنەی PeshangAcademy
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

    bot.send_photo(message.chat.id, photo_url, caption=caption, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_buttons(call):
    user_id = call.from_user.id
    first_name = call.from_user.first_name

    def add_back_button():
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("گەڕانەوە", callback_data='back'))
        return markup

    if call.data == 'my_coins':
        coins = user_coins.get(user_id, 0)
        text = f"بەڕێز {first_name}، ئەم کۆینە بۆ مەبەستی کڕینی کۆرسەکان بەکاردێت.\nتۆ ئێستا {coins} کۆینت هەیە."
        bot.send_message(call.message.chat.id, text, reply_markup=add_back_button())

    elif call.data == 'invite_link':
        link = f"https://t.me/{BOT_USERNAME}?start={user_id}"
        bot.send_message(call.message.chat.id, f"ئەمە لینکی بانگهێشتنامەکەتە:\n{link}", reply_markup=add_back_button())

    elif call.data == 'courses':
        markup = types.InlineKeyboardMarkup()
        for course, price in courses_data.items():
            markup.add(types.InlineKeyboardButton(f"{course} - کۆین {price}", callback_data=f"buy_{course}"))
        markup.add(types.InlineKeyboardButton("گەڕانەوە", callback_data='back'))
        bot.send_message(call.message.chat.id, "کۆرسە بەردەستەکان:", reply_markup=markup)

    elif call.data.startswith('buy_'):
        course_name = call.data[4:]
        course_price = courses_data.get(course_name, 0)
        coins = user_coins.get(user_id, 0)

        if coins >= course_price:
            user_coins[user_id] -= course_price
            bot.send_message(call.message.chat.id,
                             f"کۆرسی {course_name} بە سەرکەوتوویی کڕدرایە ✅\nکۆینی ماوەتەوە: {user_coins[user_id]}",
                             reply_markup=add_back_button())
        else:
            bot.send_message(call.message.chat.id,
                             f"ببوورە، تۆ {course_price} کۆین پێویستە بۆ کڕینی کۆرسی {course_name}، بەڵام تەنها {coins} کۆینت هەیە.",
                             reply_markup=add_back_button())

    elif call.data == 'all_bots':
        bot.send_message(call.message.chat.id, "ئەمە بۆتە تایبەتی ئەکادیمیای پێشەنگە:\n@PeshangTestBot", reply_markup=add_back_button())

    elif call.data == 'back':
        start(call.message)

bot.polling()
