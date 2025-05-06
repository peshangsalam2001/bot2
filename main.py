import os
import re
import telebot
from telebot import types
import yt_dlp

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
        'format': 'bestvideo+bestaudio/best',
        'merge_output_format': 'mp4',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'quiet': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
            with open(file_path, 'rb') as video_file:
                caption = f"✅ کورتە ڤیدیۆکەت بە سەرکەوتوویی داونلۆدکرا!\n{info['title']}" if is_shorts else f"✅ ڤیدیۆکەت بە سەرکەوتوویی داونلۆدکرا!\n{info['title']}"
                bot.send_video(
                    chat_id=chat_id,
                    video=video_file,
                    caption=caption
                )
            os.remove(file_path)
            bot.delete_message(chat_id, msg_id)
    except Exception as e:
    bot.edit_message_text(
        chat_id=chat_id,
        message_id=msg_id,
        text=f"❌ ببورە داونلۆدکردنەکە سەرکەوتوو نەبوو\nهەڵە: {str(e)}"
    )

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
    bot.reply_to(message, "بەڕێز تکایە لینکی ئەو ڤیدیۆی یوتوب (نەک Shorts) بنێرە کە دەتەوێ داونلۆدی بکەی.")
    bot.register_next_step_handler(message, handle_video)

@bot.message_handler(commands=['shorts'])
def shorts(message):
    if not is_member(message.from_user.id):
        return
    bot.reply_to(message, "بەڕێز تکایە لینکی ئەو کورتە ڤیدیۆی یوتوب (Shorts) بنێرە کە دەتەوێ داونلۆدی بکەی.")
    bot.register_next_step_handler(message, handle_shorts)

@bot.callback_query_handler(func=lambda call: call.data in ['video', 'shorts'])
def callback_handler(call):
    if not is_member(call.from_user.id):
        bot.answer_callback_query(call.id, "تکایە سەرەتا جۆینی کەناڵی @KurdishBots بکە و دواتر /start بنێرە.")
        return
    if call.data == 'video':
        bot.send_message(call.message.chat.id, "بەڕێز تکایە لینکی ئەو ڤیدیۆی یوتوب (نەک Shorts) بنێرە کە دەتەوێ داونلۆدی بکەی.")
        bot.register_next_step_handler(call.message, handle_video)
    elif call.data == 'shorts':
        bot.send_message(call.message.chat.id, "بەڕێز تکایە لینکی ئەو کورتە ڤیدیۆی یوتوب (Shorts) بنێرە کە دەتەوێ داونلۆدی بکەی.")
        bot.register_next_step_handler(call.message, handle_shorts)

def handle_video(message):
    if not is_member(message.from_user.id):
        return
    if not is_video_url(message.text):
        bot.reply_to(message, "ببورە، تکایە لینکی ڤیدیۆی یوتوب (نەک Shorts) بنێرە")
        return
    msg = bot.reply_to(message, "تکایە چاوەڕوانبە تا ڤیدیۆکەت بۆ داونلۆد دەکەم…")
    download_video(message.text, message.chat.id, msg.message_id, is_shorts=False)

def handle_shorts(message):
    if not is_member(message.from_user.id):
        return
    if not is_shorts_url(message.text):
        bot.reply_to(message, "ببورە، تکایە لینکی کورتە ڤیدیۆی یوتوب (Shorts) بنێرە")
        return
    msg = bot.reply_to(message, "تکایە چاوەڕوانبە تا کورتە ڤیدیۆکەت بۆ داونلۆد دەکەم…")
    download_video(message.text, message.chat.id, msg.message_id, is_shorts=True)

if __name__ == '__main__':
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    bot.infinity_polling()