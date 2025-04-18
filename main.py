from telebot import TeleBot, types

bot = TeleBot("8072279299:AAF-iMur2T62-LDnXXsQVGSg16Lqc1f1UXA")

user_coins = {}
courses_data = {
    'کۆرسی مایکرۆسۆفت ئێکسڵ': 20,
    'کۆرسی زمانی پایسۆن': 15,
    'کۆرسی مایکرۆسۆفت ئەکسس': 10,
    'کۆرسی مایکرۆسۆفت وۆرد - ئاستی سەرەتا': 0  # کۆرسی خۆڕایی
}

def get_main_menu():
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("کۆینەکانم", callback_data='my_coins'),
        types.InlineKeyboardButton("لینکی بانگهێشتنامە", callback_data='invite_link'),
        types.InlineKeyboardButton("کۆرسەکان", callback_data='courses'),
        types.InlineKeyboardButton("هەموو بۆتەکانم", callback_data='all_bots')
    )
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.chat.id
    user_first_name = message.from_user.first_name
    user_coins.setdefault(user_id, 0)
    text = f"سڵاو بەڕێز {user_first_name}، بەخێربێیت بۆ بۆتی ئەکادیمیای پێشەنگ، ئەم بۆتە تایبەتە بە کۆمەڵێک خزمەتگوزاری و زانیاری، هەر یەکە لە کڕینی کۆرس و زانینی کۆینەکانت و زانیاری تەکنەلۆجی و زۆر شتی تر\n\nبۆ هەر یەکێک لەو تایبەتمەندیانە پەنجە بە دوگمەی مەبەست بنێ"
    with open('peshang_background.jpg', 'rb') as photo:
        bot.send_photo(user_id, photo, caption=text, reply_markup=get_main_menu())

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    user_id = call.message.chat.id
    msg_id = call.message.message_id
    user_first_name = call.from_user.first_name
    chat_id = call.message.chat.id

    if call.data == "my_coins":
        text = f"بەڕێز {user_first_name}، ئەم کۆینە بۆ مەبەستی کڕینی کۆرسەکان بەکاردێت، دەتوانیت لەڕێگەی لینکی بانگهێشتنامە یاخود کڕینی کۆرسەکان بتوانی کۆینی زۆرتر کۆبکەیتەوە\n\nتۆ ئێستا {user_coins[user_id]} کۆینت هەیە"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("گەڕانەوە", callback_data='back'))
        bot.edit_message_caption(chat_id=chat_id, message_id=msg_id, caption=text, reply_markup=markup)

    elif call.data == "invite_link":
        link = f"https://t.me/Kurd2Bot_Bot?start={user_id}"
        text = f"ئەمە لینکەکەتە:\n{link}"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("گەڕانەوە", callback_data='back'))
        bot.edit_message_caption(chat_id=chat_id, message_id=msg_id, caption=text, reply_markup=markup)

    elif call.data == "courses":
        markup = types.InlineKeyboardMarkup()
        for course, price in courses_data.items():
            btn_text = f"{course} ({price} کۆین)" if price > 0 else course
            markup.add(types.InlineKeyboardButton(btn_text, callback_data=f"buy_{course}"))
        markup.add(types.InlineKeyboardButton("گەڕانەوە", callback_data='back'))
        bot.edit_message_caption(chat_id=chat_id, message_id=msg_id, caption="لیستی کۆرسەکان:", reply_markup=markup)

    elif call.data.startswith("buy_"):
        course_name = call.data.replace("buy_", "")
        price = courses_data.get(course_name, 0)

        if price == 0 and course_name == 'کۆرسی مایکرۆسۆفت وۆرد - ئاستی سەرەتا':
            bot.answer_callback_query(call.id, text="لە ئینتەرنێت دەکرێتەوە...")
            bot.edit_message_caption(chat_id=chat_id, message_id=msg_id,
                                     caption=f"ئەم کۆرسیە خۆڕاییە. تکایە کلیک بکە لەسەر ئەم لینکە:\n\nhttps://www.youtube.com/watch?v=JZ88S75tqmk&t=1s")
            return

        if user_coins[user_id] >= price:
            user_coins[user_id] -= price
            text = f"پیرۆزە! کۆرسی '{course_name}' بەسەرکەوتوویی کڕدرایەوە."
        else:
            text = "ببوورە، تۆ بڕی پێویست لە کۆینت نیە بۆ کڕینی ئەم کۆرسە."

        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("گەڕانەوە", callback_data='back'))
        bot.edit_message_caption(chat_id=chat_id, message_id=msg_id, caption=text, reply_markup=markup)

    elif call.data == "all_bots":
        text = "تەنها ئەم بۆتەیە بەردەستە:\n@PeshangTestBot"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("گەڕانەوە", callback_data='back'))
        bot.edit_message_caption(chat_id=chat_id, message_id=msg_id, caption=text, reply_markup=markup)

    elif call.data == "back":
        send_welcome(call.message)

bot.polling()
