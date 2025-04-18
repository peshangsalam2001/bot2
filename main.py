import telebot
from datetime import datetime
import random

# Replace with your bot token
BOT_TOKEN = '7686120166:AAGnrPNFIHvgXdlL3G9inlouM3f7p7VZfkY'
bot = telebot.TeleBot(BOT_TOKEN)

# Sample tech tips
tech_tips = [
    "Tip: Use a password manager to generate and store strong passwords.",
    "Tip: Update your software regularly to stay protected from vulnerabilities.",
    "Tip: Use two-factor authentication (2FA) wherever possible.",
    "Tip: Avoid clicking on suspicious links in emails or messages.",
    "Tip: Learn basic keyboard shortcuts to improve your productivity.",
    "Tip: Backup your data regularly to avoid loss in case of failure.",
    "Tip: Use incognito mode for private browsing.",
    "Tip: Learn how to use Task Manager or Activity Monitor to check system performance.",
    "Tip: Enable auto-lock on your devices to prevent unauthorized access.",
    "Tip: Use a reliable antivirus and keep it updated."
]

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Welcome to the Computer & Tech Tips Bot!\nSend /tip to get a random tech tip.")

@bot.message_handler(commands=['tip'])
def send_tech_tip(message):
    tip = random.choice(tech_tips)
    bot.send_message(message.chat.id, tip)

@bot.message_handler(func=lambda m: True)
def echo_all(message):
    bot.reply_to(message, "Type /tip to receive a random computer or tech tip.")

# Start the bot
print("Bot is running...")
bot.infinity_polling()