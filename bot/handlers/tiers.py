from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from . import utils
import config

async def tiers_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show available tiers/categories."""
    if not await utils.is_authorized(update):
        await utils.send_unauthorized(update)
        return
    
    message = config.MESSAGES["tiers_title"]
    for tier_name in config.TIERS:
        message += config.MESSAGES["tiers_item"](tier_name)
    
    await utils.send_message(update, message)

# Handler for the tiers command
tiers_handler = CommandHandler("tiers", tiers_command)
tiers_callback_handler = CallbackQueryHandler(tiers_command, pattern='^tiers$')
