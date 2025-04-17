import telebot
from telebot import types

# Replace with your Bot Token
BOT_TOKEN = '7686120166:AAGnrPNFIHvgXdlL3G9inlouM3f7p7VZfkY'
bot = telebot.TeleBot(BOT_TOKEN)

# Sample course data
courses = {
    "Excel for Beginners": "A full guide to Excel basics and tricks. 🔗 https://example.com/excel",
    "Advanced Excel": "Learn PivotTables, Macros, and PowerQuery. 🔗 https://example.com/advanced-excel",
    "Access Database": "Build your own database system. 🔗 https://example.com/access",
    "Word Tricks": "Discover secret Word formatting techniques. 🔗 https://example.com/word"
}

# Start Command
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "👋 Welcome! Type a course name or use /courses to see all available courses.")

# List All Courses
@bot.message_handler(commands=['courses'])
def list_courses(message):
    markup = types.InlineKeyboardMarkup()
    for title in courses:
        btn = types.InlineKeyboardButton(text=title, callback_data=title)
        markup.add(btn)
    bot.send_message(message.chat.id, "📚 Choose a course:", reply_markup=markup)

# Handle course selection
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    course = courses.get(call.data)
    if course:
        bot.send_message(call.message.chat.id, f"📘 *{call.data}*\n{course}", parse_mode="Markdown")

# Search by keyword
@bot.message_handler(func=lambda m: True)
def search_course(message):
    keyword = message.text.lower()
    found = False
    for title, description in courses.items():
        if keyword in title.lower():
            bot.send_message(message.chat.id, f"📘 *{title}*\n{description}", parse_mode="Markdown")
            found = True
    if not found:
        bot.send_message(message.chat.id, "❌ No matching course found. Try another keyword.")

# Start polling
bot.infinity_polling()
