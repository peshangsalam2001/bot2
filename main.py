import telebot
from telebot import types

TOKEN = '8072279299:AAF-iMur2T62-LDnXXsQVGSg16Lqc1f1UXA'
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def welcome(message):
    first_name = message.from_user.first_name

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
    first_name = call.from_user.first_name

    if call.data == 'my_coins':
        msg = f"""بەڕێز {first_name}، ئەم کۆینە بۆ مەبەستی کڕینی کۆرسەکان بەکاردێت.
دەتوانیت لە ڕێگەی لینکی بانگهێشتنامە یان کڕینی کۆرسەکان، کۆینی زۆرتر کۆبکەیتەوە.

تۆ ئێستا 0 کۆینت هەیە."""
        bot.send_message(call.message.chat.id, msg)

    elif call.data == 'invite_link':
        bot.send_message(call.message.chat.id, "ئەمە لینکی بانگهێشتنامەکەتە:\nhttps://t.me/your_bot?start=invite")

    elif call.data == 'courses':
        bot.send_message(call.message.chat.id, "ئەمە لیستی کۆرسەکانە:\n- Excel\n- Python\n- Telegram Bots\n...\nپەیوەندیم پێوە بکە بۆ زانیاری زیاتر.")

    elif call.data == 'all_bots':
        bot.send_message(call.message.chat.id, "ئەمە لیستی هەموو بۆتەکانم:\n- @ExcelKurdBot\n- @TechInfoBot\n- ...")

bot.polling()