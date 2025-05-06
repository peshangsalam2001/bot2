import os
import re
import time
import telebot
from telebot import types
import yt_dlp

TOKEN = "7245300265:AAHEDoQVR2dzjvESBU2JS9t14aRUV2rhIrI"
CHANNEL = "@KurdishBots"
ADMIN = "@MasterLordBoss"

bot = telebot.TeleBot(TOKEN)

# To track last download time per user (user_id: timestamp)
user_last_download_time = {}

def is_member(user_id):
    try:
        return bot.get_chat_member(CHANNEL, user_id).status in ['member', 'administrator', 'creator']
    except:
        return False

def is_youtube_url(url):
    return re.match(r'^(https?\:\/\/)?(www\.)?(youtube\.com|youtu\.be)\/.+', url)

def main_markup():
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("کەناڵی سەرەکی", url="https://t.me/KurdishBots")
    )
    markup.row(
        types.InlineKeyboardButton("دابەزاندنی ڤیدیۆ", callback_data='video'),
        types.InlineKeyboardButton("دابەزاندنی کورتە ڤیدیۆ", callback_data='shorts')
    )
    markup.row(
        types.InlineKeyboardButton("پەیوەندیم پێوەبکە", url=f"https://t.me/{ADMIN[1:]}")
    )
    return markup

def send_welcome(message):
    if is_member(message.from_user.id):
        name = message.from_user.first_name
        text = f"سڵاو بەڕێز {name}، بەخێربێیت بۆ بۆتی داونلۆدکردنی ڤیدیۆ و کورتە ڤیدیۆی یوتوب بە بەرزترین کوالیتی و کەمترین کات 🚀"
        bot.send_message(message.chat.id, text, reply_markup=main_markup())
    else:
        name = message.from_user.first_name
        bot.send_message(message.chat.id, f"ببورە بەڕێز {name}، سەرەتا پێویستە جۆینی کەناڵەکەمان بکەی:\n{CHANNEL}")

@bot.message_handler(commands=['start', 'سەرەکی'])
def start_or_seraki(message):
    send_welcome(message)

@bot.message_handler(func=lambda message: message.text and message.text.startswith('/'))
def other_commands(message):
    if message.text not in ['/start', '/سەرەکی']:
        bot.reply_to(message, "تکایە کۆماندی /سەرەکی بنێرە بۆ ئەوەی لیستی سەرەکیت نیشاندەم ⚠")

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data == 'video':
        bot.send_message(call.message.chat.id, "تکایە لینکی ڤیدیۆکە بنێرە بۆ ئەوەی داونلۆدی بکەم بۆت 🎬")
    elif call.data == 'shorts':
        bot.send_message(call.message.chat.id, "تکایە لینکی کورتە ڤیدیۆکە بنێرە بۆ ئەوەی داونلۆدی بکەم بۆت ⏱️")

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    user_id = message.from_user.id
    text = message.text.strip() if message.text else ""

    if is_youtube_url(text):
        if not is_member(user_id):
            bot.reply_to(message, f"ببورە بەڕێز، پێویستە سەرەتا جۆینی کەناڵەکەمان بکەیت:\n{CHANNEL}")
            return

        now = time.time()
        last_time = user_last_download_time.get(user_id, 0)
        elapsed = now - last_time

        if elapsed < 15:
            bot.reply_to(message, "تکایە ١٥ چرکە چاوەڕوانبە پاشان لینکێکی نوێ بنێرە 🚫")
            return

        user_last_download_time[user_id] = now

        # Decide if it's shorts or normal video by URL pattern
        if re.match(r'^https?://(?:www\.)?youtube\.com/shorts/', text):
            download_shorts(message)
        else:
            download_video(message)
    else:
        # For non-YouTube links or texts, show welcome message
        send_welcome(message)

def download_video(message):
    msg = bot.reply_to(message, "لینکەکە وەرگیرا تکایە چاوەڕوانبە تاکوو ڤیدیۆکەت بۆ داونلۆد دەکەم ⌛")
    download_media(message.text, message.chat.id, msg.message_id, is_shorts=False)

def download_shorts(message):
    msg = bot.reply_to(message, "لینکەکە وەرگیرا تکایە چاوەڕوانبە تاکوو کورتە ڤیدیۆکەت بۆ داونلۆد دەکەم ⌛")
    download_media(message.text, message.chat.id, msg.message_id, is_shorts=True)

def download_media(url, chat_id, msg_id, is_shorts=False):
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'merge_output_format': 'mp4',
        'quiet': True,
        'cookiefile': 'cookies.txt',  # Make sure cookies.txt is in the same folder
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
            with open(file_path, 'rb') as video_file:
                caption = f"✅ کورتە ڤیدیۆکەت بە سەرکەوتوویی داونلۆدکرا!\n{info['title']}" if is_shorts else f"✅ ڤیدیۆکەت بە سەرکەوتویی داونلۆدکرا!\n{info['title']}"
                bot.send_video(chat_id, video_file, caption=caption)
            os.remove(file_path)
            bot.delete_message(chat_id, msg_id)
    except Exception as e:
        bot.edit_message_text(f"❌ هەڵە: {str(e)}", chat_id, msg_id)

if __name__ == '__main__':
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    bot.infinity_polling()
