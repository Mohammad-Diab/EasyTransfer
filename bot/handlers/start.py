from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from . import utils
import config

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a welcome message when the command /start is issued."""
    if not await utils.is_authorized(update):
        await utils.send_unauthorized(update)
        return
    
    user_name = update.effective_user.first_name or "بك"
    welcome_message = config.MESSAGES["welcome"](user_name)
    keyboard = utils.create_main_keyboard()
    
    await utils.send_message(update, welcome_message, reply_markup=keyboard)

start_handler = CommandHandler("start", start_command)