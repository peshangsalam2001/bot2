import telebot
import yt_dlp
import os


BOT_TOKEN = "7194711538:AAF7dBt4TkfQ67TpgrAMUfK63rIscUXGjnE"
bot = telebot.TeleBot(BOT_TOKEN)

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB Telegram limit

def download_facebook_reel(url):
    ydl_opts = {
        'format': 'best',
        'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(id)s.%(ext)s'),
        'quiet': True,
        'no_warnings': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        return filename

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(
        message,
        "Send me a Facebook Reel URL and I will download the video for you! (Max 50MB)"
    )

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    url = message.text.strip()
    if not ("facebook.com/reel" in url or "facebook.com/watch" in url):
        bot.reply_to(message, "Please send a valid Facebook Reel URL.")
        return

    bot.reply_to(message, "Downloading your Reel, please wait...")

    try:
        filepath = download_facebook_reel(url)
        filesize = os.path.getsize(filepath)
        if filesize > MAX_FILE_SIZE:
            bot.reply_to(message, "Sorry, the Reel is too large to send via Telegram (over 50MB).")
            os.remove(filepath)
            return

        with open(filepath, 'rb') as video_file:
            bot.send_video(message.chat.id, video_file)
        os.remove(filepath)
    except Exception as e:
        bot.reply_to(message, f"Failed to download or send Reel: {e}")

bot.polling()