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

    # کوالیتیەکان
    qualities = [
        ("1080p", "1080"),
        ("720p", "720"),
        ("480p", "480"),
        ("360p", "360"),
        ("240p", "240"),
        ("144p", "144"),
    ]
    markup = types.InlineKeyboardMarkup(row_width=2)
    for q, qv in qualities:
        markup.add(types.InlineKeyboardButton(q, callback_data=f'quality_{qv}_{message.text}'))
    bot.reply_to(message, "تکایە بە چ کوالیتیەک دەتەوێ ڤیدیۆکە داونلۆدکەی هەڵیبژێرە", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('quality_'))
def handle_quality(call):
    if not is_member(call.from_user.id):
        bot.answer_callback_query(call.id, "تکایە سەرەتا جۆینی کەناڵی @KurdishBots بکە!")
        return
    _, quality, url = call.data.split('_', 2)
    msg = bot.send_message(call.message.chat.id, "تکایە چاوەڕوانبە تا ڤیدیۆکەت بۆ داونلۆد دەکەم…")
    ydl_opts = {
        'format': f'bestvideo[height={quality}]+bestaudio/best[height={quality}]',
        'outtmpl': f'downloads/%(title)s_{quality}p.%(ext)s',
        'merge_output_format': 'mp4',
        'quiet': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
            with open(file_path, 'rb') as video:
                bot.send_video(call.message.chat.id, video)
            os.remove(file_path)
        bot.delete_message(call.message.chat.id, msg.message_id)
    except Exception:
        bot.edit_message_text("ببورە داونلۆدکردنەکە سەرکەوتوو نەبوو", call.message.chat.id, msg.message_id)

if __name__ == '__main__':
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    bot.infinity_polling()