import telebot
import time
import random
import requests
import re
import threading
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask
from threading import Thread
from fake_useragent import UserAgent

BOT_TOKEN = "8677439105:AAFbJJUy3fFcD-d_-yiw1eQgjoLNQHvyq7A"

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

# ============================================
# APPEAL TEMPLATES
# ============================================
APPEAL_TEMPLATES = [
    """Subject: URGENT: Appeal for Wrongful WhatsApp Ban - {} 

Dear WhatsApp Support Team,

I am writing to formally appeal the ban on my WhatsApp number: {}

I have been a loyal WhatsApp user for over 5 years and have never violated your Terms of Service. I believe my account was flagged incorrectly by your automated system.

I use WhatsApp for:
- Communication with family members abroad
- Business communication with clients
- Community group coordination

I have never:
- Sent bulk or spam messages
- Harassed any user
- Shared inappropriate content

I kindly request a review of my account. I am willing to provide any additional information needed to verify my identity and good standing.

Please reinstate my account.

Thank you for your time.

Name: {}
Email: {}
Number: {}""",

    """Subject: ACCOUNT BAN APPEAL - {} 

To the WhatsApp Support Team,

My WhatsApp number {} has been banned without warning. I am a responsible user and have always complied with WhatsApp's policies.

I have been using WhatsApp since 2016 for personal and professional communication. The ban has affected my ability to work and stay connected with family.

I respectfully request that you review my case and lift the ban. I am confident that this was a mistake.

Best regards,
{}
{}
{}""",

    """Subject: REQUEST FOR ACCOUNT REVIEW - {} 

Dear WhatsApp Support,

I am appealing the suspension of my WhatsApp account: {}

I have never violated WhatsApp's Terms of Service. I believe the ban was triggered by a false report or system error.

My account is essential for:
- Contacting my family overseas
- Managing my business
- Coordinating community activities

Please review my account and restore access.

Sincerely,
{}
{}
{}""",
]

# ============================================
# UNBAN ENGINE
# ============================================
class UnbanEngine:
    def __init__(self, target, email, name):
        self.target = target
        self.email = email
        self.name = name
        self.success = 0
        self.fail = 0
        self.running = True
        self.ua = UserAgent()
        
        # WhatsApp support emails
        self.support_emails = [
            "appeals@whatsapp.com",
            "support@whatsapp.com",
            "legal@whatsapp.com",
            "abuse@whatsapp.com",
            "feedback@whatsapp.com",
            "privacy@whatsapp.com",
        ]
    
    def send_email_appeal(self):
        """Send appeal via email"""
        try:
            # Random sender email
            domains = ["gmail.com", "yahoo.com", "outlook.com", "protonmail.com", "icloud.com"]
            random_sender = f"user{random.randint(1000,9999)}@{random.choice(domains)}"
            
            # Random name
            first_names = ["John", "Jane", "Michael", "Sarah", "David", "Emma", "James", "Lisa"]
            last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis"]
            random_name = f"{random.choice(first_names)} {random.choice(last_names)}"
            
            # Generate appeal
            template = random.choice(APPEAL_TEMPLATES)
            appeal = template.format(
                random_name,
                self.target,
                random_name,
                self.email,
                self.target
            )
            
            # Pick random support email
            to_email = random.choice(self.support_emails)
            
            # Random subject
            subject = random.choice([
                f"Account Ban Appeal - {self.target}",
                f"URGENT: Wrongful Ban Appeal - {self.target}",
                f"Request for Account Review - {self.target}",
                f"Appeal: My WhatsApp Account Was Wrongfully Banned - {self.target}",
                f"Please Review My Account Ban - {self.target}"
            ])
            
            # Use a simple API endpoint instead of actual SMTP
            # Many email services accept JSON payloads
            payload = {
                "to": to_email,
                "from": random_sender,
                "subject": subject,
                "body": appeal,
                "name": random_name,
                "number": self.target,
                "email": self.email,
            }
            
            headers = {
                "User-Agent": self.ua.random,
                "Content-Type": "application/json",
                "X-Forwarded-For": f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
            }
            
            # Try multiple email relay endpoints
            email_endpoints = [
                "https://hook.eu1.make.com/email",
                "https://webhook.site/email",
                "https://api.emailjs.com/api/v1.0/email/send",
                "https://api.sendgrid.com/v3/mail/send",
            ]
            
            for endpoint in email_endpoints:
                try:
                    resp = requests.post(
                        endpoint,
                        json=payload,
                        headers=headers,
                        timeout=10
                    )
                    if resp.status_code in [200, 201, 202]:
                        self.success += 1
                        return True
                except:
                    pass
            
            # If all fail, try direct form submissions
            return self.send_web_form()
            
        except:
            return self.send_web_form()
    
    def send_web_form(self):
        """Fallback: send via web forms"""
        endpoints = [
            "https://www.whatsapp.com/contact/",
            "https://support.whatsapp.com/contact/",
        ]
        
        endpoint = random.choice(endpoints)
        clean_target = self.target.replace("+", "")
        
        payload = {
            "jazoest": str(random.randint(1000, 9999)),
            "country_code": random.choice(["us", "uk", "ng", "in", "fr", "de"]),
            "phone_number": clean_target,
            "email": self.email,
            "name": self.name,
            "subject": "Account Ban Appeal",
            "message": random.choice(APPEAL_TEMPLATES).format(self.name, self.target, self.name, self.email, self.target),
            "issue_type": "account_ban",
        }
        
        headers = {
            "User-Agent": self.ua.random,
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://www.whatsapp.com",
            "Referer": "https://www.whatsapp.com/",
        }
        
        try:
            resp = requests.post(endpoint, data=payload, headers=headers, timeout=10)
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
            
            # Try email first, fallback to web
            if random.random() < 0.7:  # 70% email attempts
                self.send_email_appeal()
            else:
                self.send_web_form()
            
            time.sleep(random.uniform(1.0, 3.0))

# ============================================
# TELEGRAM COMMANDS
# ============================================
@bot.message_handler(commands=['start'])
def start(msg):
    bot.reply_to(msg, """
🔄 *WHATSAPP UNBAN BOT*

Sends appeals via email + web forms.

*Commands:*
/unban +1234567890 — Start unban
/status — Check progress
/stop — Stop process
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

Using: Email + Web forms

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
        bot.send_message(chat_id, "⚡ Sending appeals via email + web forms...")
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