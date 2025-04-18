from telebot import TeleBot, types

TOKEN = "8072279299:AAF-iMur2T62-LDnXXsQVGSg16Lqc1f1UXA"
bot = TeleBot(TOKEN)

user_coins = {}
courses_data = {
    'کۆرسی مایکرۆسۆفت ئێکسڵ (٢٠ کۆین)': 20,
    'کۆرسی زمانی پایسۆن (١٥ کۆین)': 15,
    'کۆرسی مایکرۆسۆفت ئەکسس (١٠ کۆین)': 10,
    'کۆرسی مایکرۆسۆفت وۆرد - ئاستی سەرەتا': 0  # خۆڕایی
}

def get_welcome_message(first_name):
    return (f"سڵاو بەڕێز {first_name}، بەخێربێیت بۆ بۆتی ئەکادیمیای پێشەنگ، \n"
            f"ئەم بۆتە تایبەتە بە کۆمەڵێک خزمەتگوزاری و زانیاری، هەر یەکە لە کڕینی کۆرس و زانینی کۆینەکانت و زانیاری تەکنەلۆجی و زۆر شتی تر\n\n"
            f"بۆ هەر یەکێک لەو تایبەتمەندیانە پەنجە بە دوگمەی مەبەست بنێ")

def get_main_keyboard():
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("کۆینەکانم", callback_data="coins"),
        types.InlineKeyboardButton("لینکی بانگهێشتنامە", callback_data="invite"),
        types.InlineKeyboardButton("کۆرسەکان", callback_data="courses"),
        types.InlineKeyboardButton("هەموو بۆتەکانم", callback_data="bots")
    )
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    if user_id not in user_coins:
        user_coins[user_id] = 0

    with open('peshang.jpg', 'rb') as photo:
        bot.send_photo(message.chat.id, photo, caption=get_welcome_message(first_name), reply_markup=get_main_keyboard())

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    msg_id = call.message.message_id
    first_name = call.from_user.first_name

    if call.data == "back":
        with open('peshang.jpg', 'rb') as photo:
            bot.edit_message_media(media=types.InputMediaPhoto(photo), chat_id=chat_id, message_id=msg_id)
            bot.edit_message_caption(chat_id=chat_id, message_id=msg_id,
                                     caption=get_welcome_message(first_name), reply_markup=get_main_keyboard())

    elif call.data == "coins":
        text = (f"بەڕێز {first_name}، ئەم کۆینە بۆ مەبەستی کڕینی کۆرسەکان بەکاردێت،\n"
                f"دەتوانیت لەڕێگەی لینکی بانگهێشتنامە یاخود کڕینی کۆرسەکان بتوانی کۆینی زۆرتر کۆبکەیتەوە\n\n"
                f"تۆ ئێستا {user_coins.get(user_id, 0)} کۆینت هەیە")
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("گەڕانەوە", callback_data="back"))
        bot.edit_message_caption(chat_id=chat_id, message_id=msg_id, caption=text, reply_markup=markup)

    elif call.data == "invite":
        invite_link = "https://t.me/Kurd2Bot_Bot?start={}".format(user_id)
        text = f"ئەمە لینکەکەتە:\n{invite_link}"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("گەڕانەوە", callback_data="back"))
        bot.edit_message_caption(chat_id=chat_id, message_id=msg_id, caption=text, reply_markup=markup)

    elif call.data == "courses":
        markup = types.InlineKeyboardMarkup()
        for name, price in courses_data.items():
            markup.add(types.InlineKeyboardButton(name, callback_data=f"buy_{name}"))
        markup.add(types.InlineKeyboardButton("گەڕانەوە", callback_data="back"))
        bot.edit_message_caption(chat_id=chat_id, message_id=msg_id, caption="لیستی کۆرسەکان:", reply_markup=markup)

    elif call.data.startswith("buy_"):
        course_name = call.data.replace("buy_", "")
        price = courses_data.get(course_name, 0)

        if price == 0 and course_name == 'کۆرسی مایکرۆسۆفت وۆرد - ئاستی سەرەتا':
            bot.answer_callback_query(call.id, text="لە یوتیوب دەکرێتەوە")
            bot.edit_message_caption(chat_id=chat_id, message_id=msg_id,
                                     caption=f"ئەم کۆرسیە خۆڕاییە. کلیک بکە لەسەر ئەم لینکە:\n\nhttps://www.youtube.com/watch?v=JZ88S75tqmk&t=1s")
            return

        if user_coins[user_id] >= price:
            user_coins[user_id] -= price
            text = f"پیرۆزە! کۆرسی '{course_name}' بەسەرکەوتوویی کڕدرایەوە."
        else:
            text = "ببوورە، تۆ بڕی پێویست لە کۆینت نیە بۆ کڕینی ئەم کۆرسە."

        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("گەڕانەوە", callback_data='back'))
        bot.edit_message_caption(chat_id=chat_id, message_id=msg_id, caption=text, reply_markup=markup)

    elif call.data == "bots":
        text = "ئەمە بۆتەکەتە: @PeshangTestBot"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("گەڕانەوە", callback_data="back"))
        bot.edit_message_caption(chat_id=chat_id, message_id=msg_id, caption=text, reply_markup=markup)

bot.infinity_polling()
