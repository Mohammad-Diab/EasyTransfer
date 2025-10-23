import logging
import os
from flask import Flask, request
from telegram import Update
from telegram.ext import Application
import config
from handlers import send, status, tiers, contacts, start
from jwt_manager import jwt_manager

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

# Create the Telegram Application
application = Application.builder().token(config.BOT_TOKEN).build()

# Load JWT tokens at startup
try:
    logger.info("Loading JWT tokens from environment variables...")
    config.AUTHORIZED_TOKENS.update(jwt_manager.get_authorized_tokens())
    logger.info(f"Loaded {len(config.AUTHORIZED_TOKENS)} valid JWT tokens for authorized users")
except Exception as e:
    logger.error(f"Failed to load JWT tokens: {e}")
    raise

# Add conversation handlers
logger.info("Adding conversation handlers...")
application.add_handler(send.send_conv_handler)
application.add_handler(status.status_conv_handler)
application.add_handler(contacts.add_contact_conv_handler)
application.add_handler(contacts.delete_contact_conv_handler)
logger.info("All conversation handlers added")

# Add simple command handlers
application.add_handler(start.start_handler)
application.add_handler(tiers.tiers_handler)
application.add_handler(contacts.contacts_get_handler)

# Add callback handlers for buttons
application.add_handler(tiers.tiers_callback_handler)
application.add_handler(contacts.contacts_get_callback_handler)

# Flask route for Telegram webhook
@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    logger.info(update.to_dict()) 
    application.process_update(update)
    return "ok"

# Health check route
@app.route("/", methods=["GET"])
def index():
    return "Bot is running ✅"

if __name__ == "__main__":
    # For local development
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))