import os
from flask import Flask
from baileys import WhatsAppBot

app = Flask(__name__)

# Get config from Heroku environment
BOT_CONFIG = {
    "name": os.getenv("BOT_NAME", "MULLER SUSPENDER X1"),
    "prefix": os.getenv("BOT_PREFIX", "!"),
    "admins": os.getenv("ADMIN_NUMBERS", "").split(",")
}

class MullerBot(WhatsAppBot):
    def __init__(self):
        super().__init__(**BOT_CONFIG)
        
        # Load features
        self.load_handlers([
            AntiDeleteHandler(),
            LicenseHandler()
        ])

# Heroku web process requirement
@app.route('/')
def home():
    return "MULLER SUSPENDER X1 is running!"

if __name__ == "__main__":
    bot = MullerBot()
    
    # Run differently based on environment
    if 'DYNO' in os.environ:  # Heroku
        bot.run_in_background()
    else:  # Local
        bot.run()
