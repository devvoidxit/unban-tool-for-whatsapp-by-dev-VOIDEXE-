import telebot
import time
import random
import requests
import re
import threading
from flask import Flask
from threading import Thread
from fake_useragent import UserAgent

# ============================================
# YOUR BOT TOKEN
# ============================================
BOT_TOKEN = "8677439105:AAFbJJUy3fFcD-d_-yiw1eQgjoLNQHvyq7A"
# ============================================

bot = telebot.TeleBot(BOT_TOKEN)
active_appeals = {}

app = Flask('')

@app.route('/')
def home():
    return "🔄 WhatsApp Unban Bot"

def run():
    app.run(host='0.0.0.0', port=10000)

def keep_alive():
    t = Thread(target=run)
    t.start()

APPEAL_TEMPLATES = [
    "I am appealing the ban on my WhatsApp number. I have been a loyal user for over 5 years. I believe my account was flagged by mistake.",
    "My WhatsApp account was banned without warning. I am a small business owner and this number is my primary contact with customers.",
    "I respectfully request a review of my WhatsApp account ban. I have always followed WhatsApp's Terms of Service.",
    "I am writing to appeal the suspension of my WhatsApp number. This number is essential for my work.",
    "My WhatsApp account was disabled recently. I do not understand the reason. I use the app responsibly.",
    "I am requesting an appeal for my WhatsApp ban. I believe my account was wrongly flagged for spam.",
    "My business runs entirely through WhatsApp. The ban has crippled my operations.",
    "I am reaching out to appeal the ban on my number. I have never spammed or harassed anyone.",
    "My account was banned but I have done nothing wrong. I use WhatsApp normally.",
    "I am appealing the ban. I am not a spammer. Please help me get my account back.",
]

class UnbanEngine:
    def __init__(self, target, email, name):
        self.target = target
        self.email = email
        self.name = name
        self.success = 0
        self.fail = 0
        self.running = True
        self.ua = UserAgent()
        
        self.endpoints = [
            "https://www.whatsapp.com/contact/",
            "https://www.whatsapp.com/support/",
            "https://faq.whatsapp.com/general/account-and-profile/",
            "https://support.whatsapp.com/contact/",
            "https://www.whatsapp.com/legal/",
        ]
    
    def send_appeal(self):
        endpoint = random.choice(self.endpoints)
        clean_target = self.target.replace("+", "")
        
        payload = {
            "jazoest": str(random.randint(1000, 9999)),
            "country_code": random.choice(["us", "uk", "ng", "in"]),
            "phone_number": clean_target,
            "email": self.email,
            "name": self.name,
            "subject": random.choice([
                "Account Ban Appeal",
                "Request to Unban My Number",
                "Wrongful Ban Review Request"
            ]),
            "message": random.choice(APPEAL_TEMPLATES),
            "issue_type": random.choice([
                "account_ban", "wrongful_ban", "appeal_ban"
            ]),
            "device_info": random.choice([
                "Android 14, Samsung S24",
                "iOS 17, iPhone 15 Pro",
                "Android 13, Google Pixel 8"
            ]),
        }
        
        headers = {
            "User-Agent": self.ua.random,
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://www.whatsapp.com",
            "Referer": "https://www.whatsapp.com/",
            "X-Forwarded-For": f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
        }
        
        try:
            resp = requests.post(
                endpoint,
                data=payload,
                headers=headers,
                timeout=10,
                verify=False
            )
            
            if resp.status_code in [200, 201, 202, 302, 303, 307]:
                self.success += 1
                return True
            else:
                self.fail += 1
                return False
        except:
            self.fail += 1
            return False
    
    def appeal(self, attempts=100):
        for i in range(attempts):
            if not self.running:
                break
            self.send_appeal()
            time.sleep(random.uniform(0.5, 1.5))

@bot.message_handler(commands=['start'])
def start(msg):
    bot.reply_to(msg, """
🔄 *WHATSAPP UNBAN BOT*

*Commands:*
/unban +1234567890 — Start unban
/status — Check progress
/stop — Stop process

*Example:*
/unban +1234567890

Then provide email and name.
""", parse_mode='Markdown')

@bot.message_handler(commands=['unban'])
def unban(msg):
    args = msg.text.split()
    if len(args) < 2:
        bot.reply_to(msg, "❌ Usage: /unban +1234567890")
        return
    
    target = args[1]
    chat_id = msg.chat.id
    
    if chat_id in active_appeals:
        bot.reply_to(msg, "⚠️ Appeal already running! Use /stop")
        return
    
    bot.send_message(chat_id, "✉️ Send your email address:")
    
    if not hasattr(bot, 'user_data'):
        bot.user_data = {}
    bot.user_data[chat_id] = {'target': target, 'step': 'waiting_email'}

@bot.message_handler(commands=['stop'])
def stop(msg):
    chat_id = msg.chat.id
    if chat_id in active_appeals:
        active_appeals[chat_id].running = False
        bot.reply_to(msg, "🛑 Stopped.")
        del active_appeals[chat_id]
    else:
        bot.reply_to(msg, "❌ No active process.")

@bot.message_handler(commands=['status'])
def status(msg):
    chat_id = msg.chat.id
    if chat_id in active_appeals:
        engine = active_appeals[chat_id]
        total = engine.success + engine.fail
        rate = (engine.success/total)*100 if total > 0 else 0
        
        bot.reply_to(msg, f"""
📊 *STATUS*

Target: `{engine.target}`
Success: {engine.success}
Failed: {engine.fail}
Rate: {rate:.1f}%
""", parse_mode='Markdown')
    else:
        bot.reply_to(msg, "❌ No active process.")

@bot.message_handler(func=lambda m: True)
def handle_message(msg):
    chat_id = msg.chat.id
    text = msg.text.strip()
    
    if not hasattr(bot, 'user_data'):
        bot.user_data = {}
    
    if chat_id in bot.user_data and bot.user_data[chat_id].get('step') == 'waiting_email':
        email = text
        target = bot.user_data[chat_id]['target']
        
        if '@' not in email:
            bot.reply_to(msg, "❌ Invalid email. Send a valid email.")
            return
        
        bot.send_message(chat_id, "👤 Send your full name:")
        bot.user_data[chat_id] = {'target': target, 'email': email, 'step': 'waiting_name'}
        return
    
    if chat_id in bot.user_data and bot.user_data[chat_id].get('step') == 'waiting_name':
        name = text
        target = bot.user_data[chat_id]['target']
        email = bot.user_data[chat_id]['email']
        
        bot.user_data[chat_id] = {}
        
        bot.reply_to(msg, f"""
🔄 *UNBAN STARTED!*

Target: `{target}`
Email: `{email}`
Name: `{name}`
Appeals: 100

Use /stop to cancel.
""", parse_mode='Markdown')
        
        engine = UnbanEngine(target, email, name)
        active_appeals[chat_id] = engine
        
        threading.Thread(target=run_unban, args=(engine, chat_id)).start()
        return
    
    number_match = re.search(r'\+\d{10,15}', text)
    if number_match:
        number = number_match.group(0)
        bot.reply_to(msg, f"📱 Found `{number}`\n\nSend: `/unban {number}`", parse_mode='Markdown')

def run_unban(engine, chat_id):
    try:
        bot.send_message(chat_id, "⚡ Sending appeals...")
        engine.appeal(100)
        
        total = engine.success + engine.fail
        rate = (engine.success/total)*100 if total > 0 else 0
        
        bot.send_message(chat_id, f"""
✅ *UNBAN COMPLETE!*

✅ Success: {engine.success}
❌ Failed: {engine.fail}
📈 Rate: {rate:.1f}%

Wait 24-72 hours.
""", parse_mode='Markdown')
        
    except Exception as e:
        bot.send_message(chat_id, f"❌ Error: {str(e)[:100]}")
    
    finally:
        if chat_id in active_appeals:
            del active_appeals[chat_id]

if __name__ == "__main__":
    keep_alive()
    print("🔄 WhatsApp Unban Bot running!")
    bot.polling(none_stop=True)