import os
import re
import telebot
from telebot import types
import yt_dlp
from urllib.parse import urlparse

# رێگە لێرەوە تۆکنی بۆت دابنێ
TOKEN = "7245300265:AAHEDoQVR2dzjvESBU2JS9t14aRUV2rhIrI"
CHANNEL = "@KurdishBots"  # یوزەری کەناڵی خۆت

bot = telebot.TeleBot(TOKEN)

def is_member(user_id):
    try:
        chat_member = bot.get_chat_member(CHANNEL, user_id)
        return chat_member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        print(f"Error checking membership: {e}")
        return False

@bot.message_handler(commands=['start'])
def start(message):
    if not is_member(message.from_user.id):
        bot.reply_to(message, "تکایە سەرەتا جۆینی کەناڵی @KurdishBots بکە و دواتر /start بنێرە.")
        return
    bot.reply_to(
        message,
        f"سڵاو بەڕێز {message.from_user.first_name}\nبەخێربێت بۆ بۆتی داونلۆدکردنی ڤیدیۆ و کورتە ڤیدیۆی یوتوب\n\nبۆ بینینی سەرجەم تایبەتمەندی کۆماندەکانی بۆتەکە تکایە /help بنێرە بۆ بۆتەکە"
    )

@bot.message_handler(commands=['help'])
def help(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("ڤیدیۆ", callback_data='video'),
        types.InlineKeyboardButton("کورتە ڤیدیۆ", callback_data='shorts')
    )
    bot.reply_to(
        message,
        "بۆ داونلۆدکردنی ڤیدیۆی یوتوب تمایە کلیک لە دوگمەی ڤیدیۆ بدە یاخود کۆماندی /video بنێرە بۆ بۆتەکە\n\nبۆ داونلۆدکردنی کورتە ڤیدیۆی یوتوب تمایە کلیک لە دوگمەی کورتە ڤیدیۆ بدە یاخود کۆماندی /shorts بنێرە بۆ بۆتەکە",
        reply_markup=markup
    )

@bot.message_handler(commands=['video'])
def video(message):
    if not is_member(message.from_user.id):
        return
    bot.reply_to(message, "بەڕێز تکایە لینکی ئەو ڤیدیۆیە بنێرە کە دەتەوێ داونلۆدی بکەی.")

@bot.message_handler(commands=['shorts'])
def shorts(message):
    if not is_member(message.from_user.id):
        return
    bot.reply_to(message, "بەڕێز تکایە لینکی ئەو کورتە ڤیدیۆیە بنێرە کە دەتەوێ داونلۆدی بکەی.")

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if not is_member(call.from_user.id):
        bot.answer_callback_query(call.id, "تکایە سەرەتا جۆینی کەناڵی @KurdishBots بکە و دواتر /start بنێرە.")
        return
    if call.data == 'video':
        bot.send_message(call.message.chat.id, "بەڕێز تکایە لینکی ئەو ڤیدیۆیە بنێرە کە دەتەوێ داونلۆدی بکەی.")
    elif call.data == 'shorts':
        bot.send_message(call.message.chat.id, "بەڕێز تکایە لینکی ئەو کورتە ڤیدیۆیە بنێرە کە دەتەوێ داونلۆدی بکەی.")

def is_youtube_url(url):
    return bool(re.match(r'^https?://(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)[^\s]+', url))

@bot.message_handler(func=lambda m: True, content_types=['text'])
def handle_text(message):
    if not is_member(message.from_user.id):
        bot.reply_to(message, "تکایە سەرەتا جۆینی کەناڵی @KurdishBots بکە و دواتر /start بنێرە.")
        return
    if message.text.startswith('/'):
        bot.reply_to(message, "ببورە، تکایە /help بنێرە بۆ ئەوەی کۆماندی ڕاست و دروست بنێریت")
        return
    if not is_youtube_url(message.text):
        bot.reply_to(message, "ببورە، تکایە دڵنیابەرەوە لە ڕاست و دروستی لینکەکە")
        return

    # بۆ نمونە، تەنها ئامادەکردنی دووگمەکانی کوالیتی (دەتوانیت بە پێی سەرچاوەکانی یوتوب کوالیتییەکان بدۆزیتەوە)
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("4K", callback_data=f'quality_2160p_{message.text}'),
        types.InlineKeyboardButton("1080p", callback_data=f'quality_1080p_{message.text}'),
        types.InlineKeyboardButton("720p", callback_data=f'quality_720p_{message.text}'),
        types.InlineKeyboardButton("480p", callback_data=f'quality_480p_{message.text}'),
        types.InlineKeyboardButton("360p", callback_data=f'quality_360p_{message.text}'),
        types.InlineKeyboardButton("240p", callback_data=f'quality_240p_{message.text}'),
        types.InlineKeyboardButton("144p", callback_data=f'quality_144p_{message.text}')
    )
    bot.reply_to(
        message,
        "تکایە بە چ کوالیتیەک دەتەوێ ڤیدیۆکە داونلۆدکەی هەڵیبژێرە",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('quality_'))
def handle_quality(call):
    if not is_member(call.from_user.id):
        bot.answer_callback_query(call.id, "تکایە سەرەتا جۆینی کەناڵی @KurdishBots بکە!")
        return
    quality = call.data.split('_')[1]
    url = call.data.split('_', 2)[2]
    bot.answer_callback_query(call.id, f"داونلۆدکردنی ڤیدیۆ بە کوالیتی {quality} دەست پێدەکات...")
    bot.send_message(call.message.chat.id, f"داونلۆدکردنی ڤیدیۆ بە کوالیتی {quality} دەست پێدەکات...")

    # بۆ نمونە، داونلۆدکردنی ڤیدیۆ بە yt-dlp
    ydl_opts = {
        'format': f'bestvideo[height<={quality[:-1]}][ext=mp4]+bestaudio[ext=m4a]/best[height<={quality[:-1]}]',
        'outtmpl': f'downloads/%(title)s_{quality}.%(ext)s',
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
            with open(file_path, 'rb') as video:
                bot.send_video(call.message.chat.id, video)
    except Exception as e:
        bot.send_message(call.message.chat.id, f"هەڵەیە ڕوویدا لە داونلۆدکردنی ڤیدیۆ: {e}")

if __name__ == '__main__':
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    bot.infinity_polling()