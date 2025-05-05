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

def is_youtube_url(url):
    return bool(re.match(r'^https?://(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)[^\s]+', url))

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

@bot.message_handler(commands=['video', 'shorts'])
def video_or_shorts(message):
    if not is_member(message.from_user.id):
        return
    bot.reply_to(message, "بەڕێز تکایە لینکی ئەو ڤیدیۆیە بنێرە کە دەتەوێ داونلۆدی بکەی.")

@bot.callback_query_handler(func=lambda call: call.data in ['video', 'shorts'])
def callback_handler(call):
    if not is_member(call.from_user.id):
        bot.answer_callback_query(call.id, "تکایە سەرەتا جۆینی کەناڵی @KurdishBots بکە و دواتر /start بنێرە.")
        return
    bot.send_message(call.message.chat.id, "بەڕێز تکایە لینکی ئەو ڤیدیۆیە بنێرە کە دەتەوێ داونلۆدی بکەی.")

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

    # ناردنی نامەی چاوەڕوانی
    msg = bot.reply_to(message, "تکایە چاوەڕوانبە تا ڤیدیۆکەت بۆ داونلۆد دەکەم…")

    # ڕێکخستنەکانی yt-dlp بۆ بەرزترین کوالیتی
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'merge_output_format': 'mp4',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'quiet': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(message.text, download=True)
            file_path = ydl.prepare_filename(info)
            
            # ناردنی ڤیدیۆکە
            with open(file_path, 'rb') as video_file:
                bot.send_video(
                    chat_id=message.chat.id,
                    video=video_file,
                    caption=f"✅ ڤیدیۆکەت بە سەرکەوتوویی داونلۆدکرا!\n{info['title']}"
                )
            
            # سڕینەوەی فایلەکە دوایی ناردن
            os.remove(file_path)
            
            # سڕینەوەی نامەی چاوەڕوانی
            bot.delete_message(message.chat.id, msg.message_id)

    except Exception as e:
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=msg.message_id,
            text="❌ ببورە داونلۆدکردنەکە سەرکەوتوو نەبوو"
        )

if __name__ == '__main__':
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    bot.infinity_polling()