import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application
import config
from handlers import send, status, tiers, contacts, start
from jwt_manager import jwt_manager

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = config.BOT_TOKEN
URL = os.environ["WEBHOOK_URL"]  # e.g. https://your-app.onrender.com

# Create PTB Application
application = Application.builder().token(TOKEN).build()

# Load JWT tokens at startup
try:
    logger.info("Loading JWT tokens from environment variables...")
    config.AUTHORIZED_TOKENS.update(jwt_manager.get_authorized_tokens())
    logger.info(f"Loaded {len(config.AUTHORIZED_TOKENS)} valid JWT tokens")
except Exception as e:
    logger.error(f"Failed to load JWT tokens: {e}")
    raise

# Add handlers
application.add_handler(send.send_conv_handler)
application.add_handler(status.status_conv_handler)
application.add_handler(contacts.add_contact_conv_handler)
application.add_handler(contacts.delete_contact_conv_handler)
application.add_handler(start.start_handler)
application.add_handler(tiers.tiers_handler)
application.add_handler(contacts.contacts_get_handler)
application.add_handler(tiers.tiers_callback_handler)
application.add_handler(contacts.contacts_get_callback_handler)

# Lifespan context manager replaces on_event
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await application.initialize()
    await application.start()
    webhook_url = f"{URL}/webhook"
    await application.bot.set_webhook(webhook_url)
    logger.info(f"Webhook set to {webhook_url}")

    try:
        yield
    finally:
        # Shutdown
        await application.stop()
        await application.shutdown()

# FastAPI app with lifespan
app = FastAPI(lifespan=lifespan)

@app.post("/webhook")
async def telegram_webhook(request: Request):
    """Receive updates from Telegram and pass them to PTB."""
    data = await request.json()
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return {"ok": True}

@app.get("/")
async def health():
    return {"status": "Bot is running ✅"}