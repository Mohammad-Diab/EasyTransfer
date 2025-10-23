import logging
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

def main() -> None:
    """Start the bot."""
    # Initialize JWT tokens from environment variables at startup
    logger.info("Loading JWT tokens from environment variables...")
    try:
        # Update config with loaded tokens
        config.AUTHORIZED_TOKENS.update(jwt_manager.get_authorized_tokens())
        logger.info(f"Loaded {len(config.AUTHORIZED_TOKENS)} valid JWT tokens for authorized users")
        
    except Exception as e:
        logger.error(f"Failed to load JWT tokens: {e}")
        raise
    
    # Create the Application
    application = Application.builder().token(config.BOT_TOKEN).build()

    # Add conversation handlers (must be added before simple command handlers)
    logger.info("Adding conversation handlers...")
    application.add_handler(send.send_conv_handler)
    logger.info("send_conv_handler added")
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

    # Start the Bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
