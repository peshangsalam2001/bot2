import telebot
from telebot import types

TOKEN = '8072279299:AAF-iMur2T62-LDnXXsQVGSg16Lqc1f1UXA'
bot = telebot.TeleBot(TOKEN)

# داتابەیسی سادە بۆ نموونە
user_coins = {}

@bot.message_handler(commands=['start'])
def welcome(message):
    args = message.text.split()
    inviter_id = None

    # ئەگەر بەکارهێنەر لە ڕێگەی لینکی بانگەواز هاتووە
    if len(args) > 1:
        inviter_id = args[1]
        if inviter_id != str(message.from_user.id):
            user_coins[inviter_id] = user_coins.get(inviter_id, 0) + 1
            bot.send_message(int(inviter_id), f"بەکارهێنەری نوێیەکت بەشداربوو، 1 کۆینت زیادکرا. کۆینی ئێستات: {user_coins[inviter_id]}")

    first_name = message.from_user.first_name
    user_id = message.from_user.id
    if user_id not in user_coins:
        user_coins[user_id] = 0  # سەرجەم بەکارهێنەران دەبینریت

    welcome_text = f"""سڵاو بەڕێز {first_name}، بەخێربێیت بۆ بۆتی ئەکادیمیای پێشەنگ.
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

    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_buttons(call):
    user_id = call.from_user.id
    first_name = call.from_user.first_name

    if call.data == 'my_coins':
        coins = user_coins.get(user_id, 0)
        bot.send_message(call.message.chat.id,
                         f"بەڕێز {first_name}، ئەم کۆینە بۆ مەبەستی کڕینی کۆرسەکان بەکاردێت.\n"
                         f"دەتوانیت لە ڕێگەی لینکی بانگهێشتنامە یان کڕینی کۆرسەکان، کۆینی زۆرتر کۆبکەیتەوە.\n\n"
                         f"تۆ ئێستا {coins} کۆینت هەیە.")

    elif call.data == 'invite_link':
        user_id = call.from_user.id
        link = f"https://t.me/YOUR_BOT_USERNAME?start={user_id}"
        bot.send_message(call.message.chat.id, f"ئەمە لینکی بانگهێشتنامەکەتە:\n{link}")

    elif call.data == 'courses':
        bot.send_message(call.message.chat.id, "ئەمە لیستی کۆرسەکانە:\n- Excel\n- Python\n- Telegram Bots\n...")

    elif call.data == 'all_bots':
        bot.send_message(call.message.chat.id, "ئەمە لیستی هەموو بۆتەکانم:\n- @ExcelKurdBot\n- @TechInfoBot\n...")

bot.polling()