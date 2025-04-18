import telebot

BOT_TOKEN = '8072279299:AAF-iMur2T62-LDnXXsQVGSg16Lqc1f1UXA'
bot = telebot.TeleBot(BOT_TOKEN)

# Data store (Use database in real use)
users = {}  # Format: user_id: {"coins": int, "invited": set()}
required_coins = 3  # Coins needed to unlock the course

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    if user_id not in users:
        users[user_id] = {"coins": 0, "invited": set()}
    bot.send_message(message.chat.id,
                     f"بەخێربێیت بۆ بۆتی فرۆشتنی کۆرسەکان!\n"
                     f"بۆ بەدەست هێنانی کۆرس، پێویستە {required_coins} کۆین بەدەست بهێنیت.\n"
                     f"هەرکاتێک کەسێکت بۆ بۆت داهێنیت، ١ کۆین بەدەست دەهێنی.\n"
                     f"بەکاربهێنە: /invite")

@bot.message_handler(commands=['invite'])
def invite(message):
    user_id = message.from_user.id
    invite_link = f"https://t.me/YOUR_BOT_USERNAME?start={user_id}"
    bot.send_message(message.chat.id, f"ئەم لینکە بە هاوڕێکانت بنێرە:\n{invite_link}\nهەرکەسێک لە ڕێگای ئەم لینکە داخڵ ببێت، ١ کۆین بەدەست دەهێنی.")

@bot.message_handler(commands=['coins'])
def coins(message):
    user_id = message.from_user.id
    coins = users.get(user_id, {"coins": 0})["coins"]
    bot.send_message(message.chat.id, f"تۆ {coins} کۆینت هەیە.")

@bot.message_handler(commands=['getcourse'])
def get_course(message):
    user_id = message.from_user.id
    user_data = users.get(user_id, {"coins": 0})
    if user_data["coins"] >= required_coins:
        bot.send_message(message.chat.id, "پیرۆزە! ئەمە لینکەی کۆرسی تۆیە:\nhttps://example.com/course-link")
    else:
        bot.send_message(message.chat.id,
                         f"ببورە، پێویستە {required_coins} کۆینت هەبێت بۆ وەرگرتنی کۆرسەکە.\n"
                         f"کۆینەکەت ئێستا: {user_data['coins']}")

@bot.message_handler(func=lambda message: message.text.startswith("/start ") and len(message.text.split()) == 2)
def handle_referral(message):
    user_id = message.from_user.id
    referrer_id = int(message.text.split()[1])
    if user_id == referrer_id:
        bot.send_message(message.chat.id, "ناتوانیت خۆت ڕیفەر بکەیت!")
        return

    if user_id not in users:
        users[user_id] = {"coins": 0, "invited": set()}

    if referrer_id in users and user_id not in users[referrer_id]["invited"]:
        users[referrer_id]["coins"] += 1
        users[referrer_id]["invited"].add(user_id)
        bot.send_message(referrer_id, f"کەسێکی نوێت هێنا! ١ کۆین زیاد کرایەوە.")

    bot.send_message(message.chat.id, "بەخێربێیت! لە ئێستا دەستی پێ بکە بە هەڵگرتنی کۆین!")

# Start the bot
print("Bot is running...")
bot.infinity_polling()