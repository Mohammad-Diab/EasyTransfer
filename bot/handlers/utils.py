from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
import config
import logging

logger = logging.getLogger(__name__)

async def is_authorized(update: Update) -> bool:
    """Check if the user is authorized to use the bot."""
    user_id = get_account_id(update)
    return user_id in config.AUTHORIZED_USERS

def get_account_id(update: Update) -> int:
    """Get account_id for a telegram user. Returns telegram_user_id."""
    return update.effective_user.id

def format_api_error(operation: str, error) -> str:
    """
    Format API error with operation context.
    
    Args:
        operation: Description of the operation (e.g., "إضافة جهة الاتصال", "حذف جهة الاتصال")
        error: The APIError exception
    
    Returns:
        Formatted error message
    """
    # Get the error message from the exception
    error_msg = str(error)
    
    # Format with operation context
    return f"❌ فشل {operation}: {error_msg}"

async def send_unauthorized(update: Update) -> None:
    """Send unauthorized message to the user."""
    await send_message(update, config.MESSAGES["unauthorized"])

def create_main_keyboard() -> InlineKeyboardMarkup:
    """Create the main keyboard with available commands."""
    keyboard = [
        [InlineKeyboardButton(config.MESSAGES["button_send"], callback_data='send')],
        [InlineKeyboardButton(config.MESSAGES["button_status"], callback_data='status')],
        [InlineKeyboardButton(config.MESSAGES["button_tiers"], callback_data='tiers')],
        [
            InlineKeyboardButton(config.MESSAGES["contact_delete_button_main"], callback_data='contact_delete'),
            InlineKeyboardButton(config.MESSAGES["contact_add_button"], callback_data='contact_add')
        ],
        [InlineKeyboardButton(config.MESSAGES["button_contacts_get"], callback_data='contacts_get')]
    ]
    return InlineKeyboardMarkup(keyboard)

async def send_message(update: Update, text: str, reply_markup=None, parse_mode=None) -> None:
    """
    Unified function to send messages that works with both direct messages and callback queries.
    
    Args:
        update: The update object from Telegram
        text: The message text to send
        reply_markup: Optional reply markup (keyboard)
        parse_mode: Optional parse mode (e.g., 'HTML', 'Markdown')
    """
    try:
        if not text:
            return
        reply_text = update.message.reply_text if update.message else update.callback_query.message.edit_text

        if len(text) <= config.MAX_LEN:
            return await reply_text(text, reply_markup=reply_markup, parse_mode=parse_mode)
        
        parts = [text[i:i+config.MAX_LEN] for i in range(0, len(text), config.MAX_LEN)]
        for part in parts:
            await reply_text(part)
        return await reply_text("", reply_markup=reply_markup, parse_mode=parse_mode)
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        raise