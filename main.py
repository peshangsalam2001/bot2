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
USER_DATA_FILE = 'bot_users.json'  # New file for persistent storage

bot = telebot.TeleBot(TOKEN)

# Load persistent user data
def load_users():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                return set(data.get('users_started', []))
            except Exception:
                return set()
    return set()

def save_users(users):
    with open(USER_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump({'users_started': list(users)}, f)

# Initialize stats with persistent data
stats = {
    'users_started': load_users(),
    'valid_links': 0,
}

# Track last download time per user
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
        save_users(stats['users_started'])  # Save new user
    
    if is_member(user_id):
        name = message.from_user.first_name
        text = f"سڵاو بەڕێز {name}، بەخێربێیت بۆ بۆتی داونلۆدکردنی ڤیدیۆ و کورتە ڤیدیۆی یوتوب بە بەرزترین کوالیتی و کەمترین کات 🚀"
        bot.send_message(message.chat.id, text, reply_markup=main_markup())
    else:
        name = message.from_user.first_name
        bot.send_message(message.chat.id, f"ببورە بەڕێز {name}، سەرەتا پێویستە جۆینی کەناڵەکەمان بکەی:\n{CHANNEL}")

# New /post command handler
@bot.message_handler(commands=['post'])
def handle_post(message):
    if message.from_user.username == OWNER_USERNAME:
        msg = bot.send_message(message.chat.id, "تکایە پەیامەکەت بنێرە تاکو منیش بینێرم بۆ بەکارهێنەران")
        bot.register_next_step_handler(msg, process_post_content)
    else:
        bot.delete_message(message.chat.id, message.message_id)

def process_post_content(message):
    if message.from_user.username == OWNER_USERNAME:
        sent_count = 0
        total_users = len(stats['users_started'])
        
        # Send to all users
        for user_id in stats['users_started']:
            try:
                if message.photo:
                    bot.send_photo(user_id, message.photo[-1].file_id, caption=message.caption)
                elif message.video:
                    bot.send_video(user_id, message.video.file_id, caption=message.caption)
                else:
                    bot.send_message(user_id, message.text)
                sent_count += 1
                time.sleep(0.5)  # Avoid rate limits
            except Exception as e:
                print(f"Failed to send to {user_id}: {str(e)}")
        
        bot.send_message(message.chat.id, f"✅ پەیامەکە بە سەرکەوتوویی نێردرا بۆ {sent_count} لە {total_users} بەکارهێنەر")

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

# Rest of your existing handlers (callback_query, message handling, etc.) remain the same
# [Keep all your existing handlers for video downloading and other features here]

if __name__ == '__main__':
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    bot.infinity_polling()
