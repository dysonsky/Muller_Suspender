#!/usr/bin/env python3
"""
MULLER SUSPENDER X1 - WhatsApp Bot
One-file version with Heroku support
"""

import os
import sys
from flask import Flask, jsonify
from baileys import WhatsAppHandler, Message
from tinydb import TinyDB
import threading
import time

# ======================
# 🛠 CONFIGURATION
# ======================
class Config:
    BOT_NAME = os.getenv("BOT_NAME", "MULLER SUSPENDER X1")
    PREFIX = os.getenv("BOT_PREFIX", "!")
    ADMINS = os.getenv("ADMIN_NUMBERS", "1234567890").split(",")
    IS_HEROKU = 'DYNO' in os.environ
    SESSION_FILE = "/tmp/.muller-session" if IS_HEROKU else "./.muller-session"

# ======================
# 📦 DATABASES
# ======================
db_licenses = TinyDB('./data/licenses.json')
db_users = TinyDB('./data/users.json')

# ======================
# 🤖 BOT CORE
# ======================
class MullerBot(WhatsAppHandler):
    def __init__(self):
        super().__init__(
            session_path=Config.SESSION_FILE,
            phone_client=True
        )
        self.set_bot_profile(Config.BOT_NAME)
        print(f"⚡ {Config.BOT_NAME} initialized!")

    async def on_message(self, message: Message):
        """Main message handler"""
        try:
            if message.text.startswith(Config.PREFIX):
                await self.handle_command(message)
            elif self.is_admin(message.sender):
                await self.handle_admin_message(message)
        except Exception as e:
            print(f"⚠️ Error: {str(e)}")

    async def handle_command(self, message: Message):
        """Command processor"""
        cmd = message.text[1:].split()[0].lower()
        args = message.text.split()[1:]

        commands = {
            'activate': self.cmd_activate,
            'ban': self.cmd_ban,
            'stats': self.cmd_stats
        }

        if cmd in commands:
            await commands[cmd](message, args)

    async def cmd_activate(self, message: Message, args: list):
        """License activation"""
        if len(args) < 1:
            return await message.reply("Usage: !activate <license>")
        
        if db_licenses.contains(lambda x: x['code'] == args[0]):
            db_users.upsert(
                {'jid': message.sender, 'tier': 'premium'},
                lambda x: x['jid'] == message.sender
            )
            await message.reply("✅ License activated!")
        else:
            await message.reply("❌ Invalid license")

# ======================
# 🌐 WEB SERVER (For Heroku)
# ======================
app = Flask(__name__)

@app.route('/')
def home():
    return f"{Config.BOT_NAME} is running!"

@app.route('/status')
def status():
    return jsonify({
        "status": "online",
        "bot": Config.BOT_NAME,
        "admins": Config.ADMINS
    })

# ======================
# 🚀 LAUNCH SYSTEM
# ======================
def run_bot():
    bot = MullerBot()
    bot.run()

if __name__ == "__main__":
    if Config.IS_HEROKU:
        print("🦸 Heroku mode detected")
        # Start bot in background thread
        bot_thread = threading.Thread(target=run_bot)
        bot_thread.daemon = True
        bot_thread.start()
        
        # Start web server
        app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
    else:
        print("💻 Local mode detected")
        run_bot()
