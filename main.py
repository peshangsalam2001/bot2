import os
import re
import telebot
from telebot import types
import yt_dlp

# Replace with your actual bot token and channel username
TOKEN = "7245300265:AAHEDoQVR2dzjvESBU2JS9t14aRUV2rhIrI"
CHANNEL = "@KurdishBots"

bot = telebot.TeleBot(TOKEN)

def is_member(user_id):
    try:
        chat_member = bot.get_chat_member(CHANNEL, user_id)
        return chat_member.status in ['member', 'administrator', 'creator']
    except Exception:
        return False

def is_shorts_url(url):
    return bool(re.match(r'^https?://(?:www\.)?youtube\.com/shorts/[^\s]+', url))

def is_video_url(url):
    return bool(re.match(r'^https?://(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)[^\s]+', url))

def download_video(url, chat_id, msg_id, is_shorts=False):
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'merge_output_format': 'mp4',
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }],
        'quiet': False,
        'verbose': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
            with open(file_path, 'rb') as video_file:
                caption = f"✅ Shorts video downloaded successfully!\n{info['title']}" if is_shorts else f"✅ Video downloaded successfully!\n{info['title']}"
                bot.send_video(
                    chat_id=chat_id,
                    video=video_file,
                    caption=caption,
                    supports_streaming=True
                )
            os.remove(file_path)
            bot.delete_message(chat_id, msg_id)
    except Exception as e:
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=msg_id,
            text=f"❌ Sorry, download failed.\nReason: {str(e)}"
        )

@bot.message_handler(commands=['start'])
def start(message):
    if not is_member(message.from_user.id):
        bot.reply_to(message, f"Please join {CHANNEL} first, then send /start again.")
        return
    bot.reply_to(
        message,
        f"Hello {message.from_user.first_name}!\nWelcome to the YouTube Video Downloader Bot.\n\nUse /help to see all commands."
    )

@bot.message_handler(commands=['help'])
def help(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("Video", callback_data='video'),
        types.InlineKeyboardButton("Shorts", callback_data='shorts')
    )
    bot.reply_to(
        message,
        "To download a YouTube video, click the 'Video' button or send /video.\n\nTo download a YouTube Shorts video, click the 'Shorts' button or send /shorts.",
        reply_markup=markup
    )

@bot.message_handler(commands=['video'])
def video(message):
    if not is_member(message.from_user.id):
        return
    bot.reply_to(message, "Please send the YouTube video link (not Shorts).")
    bot.register_next_step_handler(message, handle_video)

@bot.message_handler(commands=['shorts'])
def shorts(message):
    if not is_member(message.from_user.id):
        return
    bot.reply_to(message, "Please send the YouTube Shorts link.")
    bot.register_next_step_handler(message, handle_shorts)

@bot.callback_query_handler(func=lambda call: call.data in ['video', 'shorts'])
def callback_handler(call):
    if not is_member(call.from_user.id):
        bot.answer_callback_query(call.id, f"Please join {CHANNEL} first, then try again.")
        return
    if call.data == 'video':
        bot.send_message(call.message.chat.id, "Please send the YouTube video link (not Shorts).")
        bot.register_next_step_handler(call.message, handle_video)
    elif call.data == 'shorts':
        bot.send_message(call.message.chat.id, "Please send the YouTube Shorts link.")
        bot.register_next_step_handler(call.message, handle_shorts)

def handle_video(message):
    if not is_member(message.from_user.id):
        return
    if not is_video_url(message.text):
        bot.reply_to(message, "Please send a valid YouTube video link (not Shorts).")
        return
    msg = bot.reply_to(message, "Please wait, downloading your video...")
    download_video(message.text, message.chat.id, msg.message_id, is_shorts=False)

def handle_shorts(message):
    if not is_member(message.from_user.id):
        return
    if not is_shorts_url(message.text):
        bot.reply_to(message, "Please send a valid YouTube Shorts link.")
        return
    msg = bot.reply_to(message, "Please wait, downloading your Shorts video...")
    download_video(message.text, message.chat.id, msg.message_id, is_shorts=True)

if __name__ == '__main__':
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    bot.infinity_polling()
