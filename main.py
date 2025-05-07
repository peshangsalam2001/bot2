import os
import re
import time
import requests
import telebot
from telebot import types
import yt_dlp

TOKEN = "8136969513:AAGkfHTKjxZJa9nvANKHUHW1LutPP3wDBCQ"
CHANNEL = "@KurdishBots"
ADMIN = "@MasterLordBoss"
OWNER_USERNAME = "MasterLordBoss"  # بێ @

bot = telebot.TeleBot(TOKEN)

user_last_download_time = {}

stats = {
    'users_started': set(),
    'valid_links': 0,
}

TUTORIAL_VIDEO_URL = "https://media-hosting.imagekit.io/a031c091769643da/IMG_4141%20(1).MP4?Expires=1841246907&Key-Pair-Id=K2ZIVPTIP2VGHC&Signature=z6BkaPkTwhTwjl-QZw6VNroAuS7zbxxIboZclk8Ww1GTQpxK~M-03JNLXt5Ml6pReIyvxJGGKBGX60~uGI2S5Tev3QtMHz3hIa7iPTQIrfv1p32oTvwyycnFfvecpFAofB-4qGSvZ5YsynhnrpUJT-fH25ROpkGnj9xMo87KWlrd6E1G9sWP5PNwpnLkRMkoh2uZLyWA935JPLX0bJMRGdovqmrORlp7XvxoOom2vHg2zydq1JSDVDlbxGFsM3guN8GWSPSM-pfOymZfJY-r~ajDT8sD~fjDCUwji~zW~LCqLTYdwHhglJXmtOStjsmeXqn4JOU2Q85LtIM~LHRTgA__"

def is_member(user_id):
    try:
        return bot.get_chat_member(CHANNEL, user_id).status in ['member', 'administrator', 'creator']
    except Exception:
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
    markup.row(
        types.InlineKeyboardButton("چۆنیاتی بەکارهێنانی بۆتەکە", callback_data='howto')
    )
    return markup

def send_welcome(message):
    user_id = message.from_user.id
    if user_id not in stats['users_started']:
        stats['users_started'].add(user_id)
    if is_member(user_id):
        name = message.from_user.first_name
        text = f"سڵاو بەڕێز {name}، بەخێربێیت بۆ بۆتی داونلۆدکردنی ڤیدیۆ و کورتە ڤیدیۆی یوتوب بە بەرزترین کوالیتی و کەمترین کات 🚀"
        bot.send_message(message.chat.id, text, reply_markup=main_markup())
    else:
        name = message.from_user.first_name
        bot.send_message(message.chat.id, f"ببورە بەڕێز {name}، سەرەتا پێویستە جۆینی کەناڵەکەمان بکەی:\n{CHANNEL}")

@bot.message_handler(commands=['start', 'سەرەکی'])
def start_or_seraki(message):
    send_welcome(message)

@bot.message_handler(commands=['stats'])
def stats_command(message):
    if message.from_user.username == OWNER_USERNAME:
        user_count = len(stats['users_started'])
        valid_links = stats['valid_links']
        text = (
            f"📊 نوێترین زانیاری بۆت:\n"
            f"👥 ژمارەی بەکارهێنەران: {user_count}\n"
            f"🎬 ژمارەی لینکی ڤیدیۆی دروست داواکراوە: {valid_links}\n"
            f"⏰ کاتی داواکاری: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}"
        )
        bot.reply_to(message, text)
    else:
        bot.reply_to(message, "فەرمانەکە تەنها بۆ خاوەنی بۆتە.")

@bot.message_handler(func=lambda message: message.text and message.text.startswith('/'))
def other_commands(message):
    if message.text not in ['/start', '/سەرەکی', '/stats']:
        bot.reply_to(message, "تکایە کۆماندی /سەرەکی بنێرە بۆ ئەوەی لیستی سەرەکیت نیشاندەم ⚠")

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data == 'video':
        bot.send_message(call.message.chat.id, "تکایە لینکی ڤیدیۆکە بنێرە بۆ ئەوەی داونلۆدی بکەم بۆت 🎬")
    elif call.data == 'shorts':
        bot.send_message(call.message.chat.id, "تکایە لینکی کورتە ڤیدیۆکە بنێرە بۆ ئەوەی داونلۆدی بکەم بۆت ⏱️")
    elif call.data == 'howto':
        caption = "ئەم ڤیدیۆیە فێرکاری چۆنیەتی بەکارهێنانی بۆتەکەیە ✅"
        try:
            video_data = download_video_from_url(TUTORIAL_VIDEO_URL)
            if video_data:
                bot.send_video(call.message.chat.id, video_data, caption=caption)
            else:
                bot.send_message(call.message.chat.id, "❌ نەتوانرا ڤیدیۆکە باربکەم، تکایە دووبارە هەوڵ بدە.")
        except Exception as e:
            bot.send_message(call.message.chat.id, f"❌ هەڵە لە ناردنی ڤیدیۆ: {str(e)}")

def download_video_from_url(url):
    import io
    try:
        response = requests.get(url, stream=True, timeout=60)
        response.raise_for_status()
        video_bytes = io.BytesIO(response.content)
        video_bytes.name = "tutorial_video.mp4"
        return video_bytes
    except Exception as e:
        print(f"Error downloading tutorial video: {e}")
        return None

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
        stats['valid_links'] += 1

        if re.match(r'^https?://(?:www\.)?youtube\.com/shorts/', text):
            download_shorts(message)
        else:
            download_video(message)
    else:
        send_welcome(message)

def download_video(message):
    msg = bot.reply_to(message, "لینکەکە وەرگیرا تکایە چاوەڕوانبە تاکوو ڤیدیۆکەت بۆ داونلۆد دەکەم ⌛")
    download_media(message.text, message.chat.id, msg.message_id, is_shorts=False)

def download_shorts(message):
    msg = bot.reply_to(message, "لینکەکە وەرگیرا تکایە چاوەڕوانبە تاکوو کورتە ڤیدیۆکەت بۆ داونلۆد دەکەم ⌛")
    download_media(message.text, message.chat.id, msg.message_id, is_shorts=True)

def download_media(url, chat_id, msg_id, is_shorts=False):
    import math

    quality_options = [
        'bestvideo[height<=1080]+bestaudio/best',
        'bestvideo[height<=720]+bestaudio/best',
        'bestvideo[height<=480]+bestaudio/best',
        'bestvideo[height<=360]+bestaudio/best',
    ]

    max_size = 50 * 1024 * 1024  # 50 MB limit

    last_error = None
    for fmt in quality_options:
        ydl_opts = {
            'format': fmt,
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'merge_output_format': 'mp4',
            'quiet': True,
            'cookiefile': 'cookies.txt',
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                file_path = ydl.prepare_filename(info)
                file_size = os.path.getsize(file_path)

                if file_size <= max_size:
                    with open(file_path, 'rb') as video_file:
                        caption = f"✅ کورتە ڤیدیۆکەت بە سەرکەوتوویی داونلۆدکرا!\n{info['title']}" if is_shorts else f"✅ ڤیدیۆکەت بە سەرکەوتویی داونلۆدکرا!\n{info['title']}"
                        bot.send_video(chat_id, video_file, caption=caption)
                    os.remove(file_path)
                    bot.delete_message(chat_id, msg_id)
                    return
                else:
                    os.remove(file_path)
                    last_error = f"ڤیدیۆکە لە کوالیتی {fmt} زیاتر لە 50MB بوو ({math.ceil(file_size/(1024*1024))}MB)"
        except Exception as e:
            last_error = str(e)

    error_msg = f"❌ ببورە، نەتوانرا ڤیدیۆکە بە کوالیتی کەمتر لە 50MB داونلۆد بکەم.\n{last_error if last_error else ''}"
    bot.edit_message_text(error_msg, chat_id, msg_id)

if __name__ == '__main__':
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    bot.infinity_polling()
