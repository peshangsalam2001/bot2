import telebot
from telebot import types

TOKEN = '8072279299:AAF-iMur2T62-LDnXXsQVGSg16Lqc1f1UXA'
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        types.InlineKeyboardButton("ووضو - تەواوکردن", callback_data="wudu"),
        types.InlineKeyboardButton("نوێژکردن", callback_data="prayer"),
        types.InlineKeyboardButton("کاتەکانی نوێژ", callback_data="times")
    )
    bot.send_message(message.chat.id, "بەخێربێیت بۆ فێربوونی نوێژ، تکایە یەکێک لە دوگمەکان هەڵبژێرە:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    if call.data == "wudu":
        bot.send_message(call.message.chat.id, "چۆنیەتی تەواوکردن (ووضو):\n١. دەتەوێت دەستی ڕاستت وەشێیت...\n٢. دەم، پێ، گوێ، پێشانی، وە هتد.")
    elif call.data == "prayer":
        bot.send_message(call.message.chat.id, "چۆنیەتی نوێژکردن:\n١. نیت\n٢. تکبیرە\n٣. قراەتەکان و ڕکوع و سەجدە...\nوە هتد.")
    elif call.data == "times":
        bot.send_message(call.message.chat.id, "کاتەکانی نوێژ:\n- بەیانی: 5:00\n- نیوڕۆ: 12:30\n- ئێوارە: 3:45\n- مەغریب: 6:10\n- عیشا: 7:30")

bot.polling()