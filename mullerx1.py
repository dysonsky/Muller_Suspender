#!/usr/bin/env python3
"""
MULLER SUSPENDER X1 - Ultimate WhatsApp Bot
with Dyson Session Management & MULLERTECH Security
"""

import os
import json
import base64
import hashlib
import threading
import time
from flask import Flask, request, jsonify, render_template_string, send_file
from baileys import WhatsAppHandler, Message
import qrcode
from io import BytesIO
from tinydb import TinyDB, Query
import zipfile
from datetime import datetime, timedelta

# ======================
# 🔐 SECURITY CONFIG
# ======================
MULLERTECH_PASSWORD = os.getenv("MULLERTECH_PW", "MULLERTECH")  # Change in production!
ADMIN_KEY = hashlib.sha256(MULLERTECH_PASSWORD.encode()).hexdigest()

# ======================
# 🛠 BOT CONFIGURATION
# ======================
class Config:
    BOT_NAME = "MULLER SUSPENDER X1"
    PREFIX = "!"
    ADMINS = ["1234567890@s.whatsapp.net"]  # Your number
    SESSION_FILE = "./muller_session.json"
    DB_FILE = "./data/muller_db.json"
    PORT = 5000
    SESSION_ID = None
    AUTH_REQUIRED = True

# ======================
# 📦 DATABASE SETUP
# ======================
os.makedirs('./data', exist_ok=True)
db = TinyDB(Config.DB_FILE)
auth_db = db.table('auth')
licenses = db.table('licenses')
users = db.table('users')

# ======================
# 🌐 CONTROL PANEL
# ======================
app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>{{ bot_name }} - MULLERTECH</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .panel { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 20px; }
        .btn { background: #4CAF50; color: white; padding: 10px 15px; border: none; border-radius: 4px; cursor: pointer; text-decoration: none; display: inline-block; }
        .session-box { background: #1e1e1e; color: #00ff00; padding: 15px; border-radius: 4px; font-family: monospace; margin: 15px 0; word-break: break-all; }
        .status { padding: 10px; border-radius: 4px; margin: 15px 0; }
        .online { background: #e1f7e1; color: #2e7d32; }
        .offline { background: #ffebee; color: #c62828; }
        .hidden { display: none; }
    </style>
</head>
<body>
    {% if not authenticated %}
    <div class="panel" style="max-width: 500px; margin: 50px auto; text-align: center;">
        <h2>🔒 MULLERTECH AUTHENTICATION</h2>
        <form id="authForm" action="/auth" method="POST" style="margin-top: 20px;">
            <input type="password" name="password" placeholder="Enter MULLERTECH Password" style="width: 100%; padding: 10px; margin-bottom: 15px; border: 1px solid #ddd; border-radius: 4px;">
            <button type="submit" class="btn">Authenticate</button>
            {% if auth_error %}<p style="color: #dc3545; margin-top: 15px;">{{ auth_error }}</p>{% endif %}
        </form>
    </div>
    {% else %}
    <div style="max-width: 800px; margin: 0 auto;">
        <h1 style="text-align: center;">🤖 {{ bot_name }} CONTROL PANEL</h1>
        
        <div class="panel">
            <h2>📊 Bot Status</h2>
            <div class="status {{ 'online' if connected else 'offline' }}">
                Status: {{ 'CONNECTED' if connected else 'DISCONNECTED' }}
            </div>
        </div>

        <div class="panel">
            <h2>🔐 Session Management</h2>
            {% if qr_code %}
                <p>Scan this QR code with WhatsApp:</p>
                <img src="data:image/png;base64,{{ qr_code }}" width="250" style="display: block; margin: 0 auto;">
            {% else %}
                <p>Current Session ID:</p>
                <div class="session-box">{{ session_id }}</div>
                <button class="btn" onclick="copySession()">Copy Session ID</button>
                <button class="btn" style="background: #dc3545;" onclick="restartBot()">Restart Bot</button>
            {% endif %}
        </div>

        <div class="panel">
            <h2>🚀 Deployment</h2>
            <p>Download complete bot package:</p>
            <a href="/download" class="btn">Download MULLER-X1.zip</a>
        </div>

        <div class="panel">
            <h2>🔑 License Generator</h2>
            <form id="licenseForm" onsubmit="generateLicense(event)">
                <input type="number" id="days" placeholder="Days" value="30" style="padding: 8px; margin-right: 10px;">
                <select id="tier" style="padding: 8px; margin-right: 10px;">
                    <option value="basic">Basic</option>
                    <option value="premium">Premium</option>
                    <option value="vip">VIP</option>
                </select>
                <button type="submit" class="btn">Generate</button>
            </form>
            <div id="licenseResult" class="session-box hidden"></div>
        </div>
    </div>
    {% endif %}

    <script>
        function copySession() {
            const sessionText = document.querySelector('.session-box').innerText;
            navigator.clipboard.writeText(sessionText);
            alert('Session ID copied!');
        }

        function restartBot() {
            if(confirm('Restart bot?')) {
                fetch('/api/restart', {
                    method: 'POST',
                    headers: { 'X-Admin-Key': '{{ admin_key }}' }
                }).then(r => r.json()).then(d => {
                    if(d.status === 'restarting') {
                        alert('Bot restarting...');
                        setTimeout(() => location.reload(), 3000);
                    }
                });
            }
        }

        function generateLicense(e) {
            e.preventDefault();
            fetch('/api/license', {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'X-Admin-Key': '{{ admin_key }}'
                },
                body: JSON.stringify({
                    days: document.getElementById('days').value,
                    tier: document.getElementById('tier').value
                })
            }).then(r => r.json()).then(d => {
                const box = document.getElementById('licenseResult');
                box.innerHTML = `LICENSE: ${d.code}<br>TIER: ${d.tier}<br>EXPIRES: ${d.expiry}`;
                box.classList.remove('hidden');
            });
        }
    </script>
</body>
</html>
"""

# ======================
# 🤖 BOT CORE
# ======================
class MullerBot(WhatsAppHandler):
    def __init__(self):
        super().__init__(session_path=Config.SESSION_FILE)
        self.qr_code = None
        self.connected = False
        self.commands = {
            'activate': self.cmd_activate,
            'ban': self.cmd_ban,
            'addadmin': self.cmd_addadmin
        }
        
    async def on_qr(self, qr):
        img = qrcode.make(qr)
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        self.qr_code = base64.b64encode(buffered.getvalue()).decode()
        
    async def on_ready(self):
        self.connected = True
        Config.SESSION_ID = self.get_session_id()
        print(f"✅ {Config.BOT_NAME} is ONLINE!")
        
    async def on_message(self, message: Message):
        if Config.AUTH_REQUIRED and message.sender not in users and not self.is_admin(message.sender):
            return await message.reply("🔒 This bot is password protected. Send !activate LICENSE_CODE")
            
        if message.text.startswith(Config.PREFIX):
            cmd = message.text[1:].split()[0].lower()
            args = message.text.split()[1:]
            if cmd in self.commands:
                await self.commands[cmd](message, args)
    
    async def cmd_activate(self, message, args):
        if not args: return await message.reply("Usage: !activate LICENSE_CODE")
        license = licenses.get(Query().code == args[0])
        if license:
            users.upsert({
                'jid': message.sender,
                'tier': license['tier'],
                'expiry': license['expiry']
            }, Query().jid == message.sender)
            await message.reply(f"✅ {license['tier'].upper()} features activated!")
        else:
            await message.reply("❌ Invalid license")
    
    async def cmd_addadmin(self, message, args):
        if not self.is_admin(message.sender):
            return await message.reply("❌ Admin only!")
        Config.ADMINS.append(args[0])
        await message.reply(f"✅ Added admin: {args[0]}")
    
    def is_admin(self, jid):
        return
