import telebot
from telebot import types

TOKEN = '8072279299:AAF-iMur2T62-LDnXXsQVGSg16Lqc1f1UXA'
bot = telebot.TeleBot(TOKEN)

# داتابەیسی سادە: کۆینەکان و بانگەوازکردن
user_coins = {}
invited_users = set()

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    args = message.text.split()

    # چاککردنی ئەوەی ناوی بەکارهێنەر تۆمار نەکراو بوو
    if user_id not in user_coins:
        user_coins[user_id] = 0

    # بەکارهێنەری نوێ لە ڕێگەی بانگەواز
    if len(args) > 1:
        inviter_id = args[1]
        if inviter_id != str(user_id):  # بەکارهێنەری خۆی نەبێ
            key = f"{inviter_id}_{user_id}"
            if key not in invited_users:
                invited_users.add(key)
                user_coins[int(inviter_id)] = user_coins.get(int(inviter_id), 0) + 1
                bot.send_message(int(inviter_id),
                                 f"سڵاو! کەسێک لەڕێگەی لینکی بانگهێشتنامەکەت هاتە ناو بۆتەکە. 1 کۆینت زیاد کرا. کۆینی ئێستات: {user_coins[int(inviter_id)]}")

    # ناردنی نامەی سەرەکی و دوگمەکان
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
                         f"تۆ ئێستا {coins} کۆینت هەیە.")

    elif call.data == 'invite_link':
        link = f"https://t.me/Bot2Kurd_Bot?start={user_id}"
        bot.send_message(call.message.chat.id, f"ئەمە لینکی بانگهێشتنامەکەتە:\n{link}")

    elif call.data == 'courses':
        bot.send_message(call.message.chat.id, "ئەمە لیستی کۆرسەکانە:\n- Excel\n- Python\n- Telegram Bots\n...")

    elif call.data == 'all_bots':
        bot.send_message(call.message.chat.id, "ئەمە لیستی هەموو بۆتەکانم:\n- @ExcelKurdBot\n- @TechInfoBot\n...")

bot.polling()