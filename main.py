import os
import re
import time
import json
import requests
import telebot
from telebot import types
import yt_dlp

TOKEN = "8136969513:AAGkfHTKjxZJa9nvANKHUHW1LutPP3wDBCQ"
CHANNEL = "@KurdishBots"
ADMIN = "@MasterLordBoss"
OWNER_USERNAME = "MasterLordBoss"
USER_DATA_FILE = 'bot_users.json'

bot = telebot.TeleBot(TOKEN)

# Persistent user storage functions
def load_users():
    if os.path.exists(USER_DATA_FILE):
        try:
            with open(USER_DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return set(data.get('users_started', []))
        except Exception:
            return set()
    return set()

def save_users(users):
    with open(USER_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump({'users_started': list(users)}, f)

# Initialize stats
stats = {
    'users_started': load_users(),
    'valid_links': 0,
}

user_last_download_time = {}
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
    markup.row(types.InlineKeyboardButton("کەناڵی سەرەکی", url="https://t.me/KurdishBots"))
    markup.row(
        types.InlineKeyboardButton("دابەزاندنی ڤیدیۆ", callback_data='video'),
        types.InlineKeyboardButton("دابەزاندنی کورتە ڤیدیۆ", callback_data='shorts')
    )
    markup.row(types.InlineKeyboardButton("پەیوەندیم پێوەبکە", url=f"https://t.me/{ADMIN[1:]}"))
    markup.row(types.InlineKeyboardButton("چۆنیاتی بەکارهێنانی بۆتەکە", callback_data='howto'))
    return markup

def send_welcome(message):
    user_id = message.from_user.id
    if user_id not in stats['users_started']:
        stats['users_started'].add(user_id)
        save_users(stats['users_started'])
    
    if is_member(user_id):
        name = message.from_user.first_name
        text = f"سڵاو بەڕێز {name}، بەخێربێیت بۆ بۆتی داونلۆدکردنی ڤیدیۆ و کورتە ڤیدیۆی یوتوب بە بەرزترین کوالیتی و کەمترین کات 🚀"
        bot.send_message(message.chat.id, text, reply_markup=main_markup())
    else:
        name = message.from_user.first_name
        bot.send_message(message.chat.id, f"ببورە بەڕێز {name}، سەرەتا پێویستە جۆینی کەناڵەکەمان بکەی:\n{CHANNEL}")

@bot.message_handler(commands=['start', 'سەرەکی'])
def start_handler(message):
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
        bot.delete_message(message.chat.id, message.message_id)

@bot.message_handler(commands=['post'])
def post_command(message):
    if message.from_user.username == OWNER_USERNAME:
        msg = bot.send_message(message.chat.id, "تکایە پەیامەکەت بنێرە تاکو منیش بینێرم بۆ بەکارهێنەران")
        bot.register_next_step_handler(msg, process_post)
    else:
        bot.delete_message(message.chat.id, message.message_id)

def process_post(message):
    if message.from_user.username == OWNER_USERNAME:
        sent = 0
        errors = 0
        total = len(stats['users_started'])
        
        for user_id in stats['users_started']:
            try:
                if message.content_type == 'text':
                    bot.send_message(user_id, message.text)
                elif message.content_type == 'photo':
                    bot.send_photo(user_id, message.photo[-1].file_id, caption=message.caption)
                elif message.content_type == 'video':
                    bot.send_video(user_id, message.video.file_id, caption=message.caption)
                sent += 1
                time.sleep(0.5)
            except Exception as e:
                errors += 1
        bot.send_message(message.chat.id, f"✅ نێردرا بۆ {sent} بەکارهێنەر | شکستی هێنا بۆ {errors}")

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data == 'video':
        bot.send_message(call.message.chat.id, "تکایە لینکی ڤیدیۆکە بنێرە بۆ ئەوەی داونلۆدی بکەم بۆت 🎬")
    elif call.data == 'shorts':
        bot.send_message(call.message.chat.id, "تکایە لینکی کورتە ڤیدیۆکە بنێرە بۆ ئەوەی داونلۆدی بکەم بۆت ⏱️")
    elif call.data == 'howto':
        try:
            video = requests.get(TUTORIAL_VIDEO_URL, stream=True).content
            bot.send_video(call.message.chat.id, video, caption="ئەم ڤیدیۆیە فێرکاری چۆنیەتی بەکارهێنانی بۆتەکەیە ✅")
        except Exception as e:
            bot.send_message(call.message.chat.id, f"❌ هەڵە لە ناردنی ڤیدیۆ: {str(e)}")

@bot.message_handler(func=lambda message: True)
def message_handler(message):
    user_id = message.from_user.id
    text = message.text.strip()
    
    if not is_member(user_id):
        bot.reply_to(message, f"ببورە بەڕێز، پێویستە سەرەتا جۆینی کەناڵەکەمان بکەیت:\n{CHANNEL}")
        return
    
    if is_youtube_url(text):
        now = time.time()
        if user_id in user_last_download_time and (now - user_last_download_time[user_id]) < 15:
            bot.reply_to(message, "تکایە ١٥ چرکە چاوەڕوانبە پاشان لینکێکی نوێ بنێرە 🚫")
            return
        
        user_last_download_time[user_id] = now
        stats['valid_links'] += 1
        
        if 'shorts' in text:
            download_shorts(message)
        else:
            download_video(message)
    else:
        send_welcome(message)

def download_video(message):
    msg = bot.reply_to(message, "لینکەکە وەرگیرا تکایە چاوەڕوانبە تاکوو ڤیدیۆکەت بۆ داونلۆد دەکەم ⌛")
    process_download(message.text, msg.chat.id, msg.message_id, False)

def download_shorts(message):
    msg = bot.reply_to(message, "لینکەکە وەرگیرا تکایە چاوەڕوانبە تاکوو کورتە ڤیدیۆکەت بۆ داونلۆد دەکەم ⌛")
    process_download(message.text, msg.chat.id, msg.message_id, True)

def process_download(url, chat_id, msg_id, is_shorts):
    formats = [
        'bestvideo[height<=1080]+bestaudio/best',
        'bestvideo[height<=720]+bestaudio/best',
        'bestvideo[height<=480]+bestaudio/best',
        'bestvideo[height<=360]+bestaudio/best',
    ]
    
    for fmt in formats:
        try:
            with yt_dlp.YoutubeDL({
                'format': fmt,
                'outtmpl': 'downloads/%(title)s.%(ext)s',
                'quiet': True
            }) as ydl:
                info = ydl.extract_info(url, download=True)
                file_path = ydl.prepare_filename(info)
                
                if os.path.getsize(file_path) > 50 * 1024 * 1024:
                    os.remove(file_path)
                    continue
                
                with open(file_path, 'rb') as f:
                    caption_type = "کورتە ڤیدیۆ" if is_shorts else "ڤیدیۆ"
                    bot.send_video(chat_id, f, caption=f"✅ {caption_type}کەت بە سەرکەوتوویی داونلۆدکرا!\n{info['title']}")
                os.remove(file_path)
                bot.delete_message(chat_id, msg_id)
                return
        except Exception as e:
            continue
    
    bot.edit_message_text("❌ نەتوانرا ڤیدیۆکە دابەزێنرێت لەبەر قەبارەی گەورە یان هەڵەیەک ڕوویدا", chat_id, msg_id)

if __name__ == '__main__':
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    bot.infinity_polling()
