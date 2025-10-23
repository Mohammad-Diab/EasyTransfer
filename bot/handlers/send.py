from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters
)
from . import api_utils
import config
import logging
from . import utils

# Configure logging
logger = logging.getLogger(__name__)

# Conversation states
TIER, SEND_AMOUNT, PHONE, CONFIRM = range(4)

def find_nearest_tier(amount: float) -> float:
    """Find the nearest tier within 20% range of the given amount."""
    if amount <= 0:
        return -1

    nearest = -1
    for tier in config.TIERS:
        if abs(tier - amount) <= tier * 0.2:  # Within 20% range
            if nearest == -1 or abs(tier - amount) < abs(nearest - amount):
                nearest = tier

    return nearest

def validate_and_get_contact_info(contact_input: str, account_id: str) -> str:
    """
    Validate contact input and return (contact_name, phone_number).

    Returns None if contact is invalid.
    Supports both contact names and direct phone numbers.
    """
    try:
        response = api_utils.get_contacts(account_id)
        contacts = response.get('data', response.get('contacts', []))

        # Check if input matches any existing contact name or phone
        for contact in contacts:
            contact_name_db = contact.get('name', '')
            contact_phone_db = contact.get('phone_number', '')

            # Check if input matches contact name (case insensitive)
            if contact_name_db.lower() == contact_input.lower():
                return contact_phone_db

        # If not found in contacts, check if it's a valid phone number
        if contact_input.isdigit() and len(contact_input) >= 10:
            return contact_input

        return ""  # Invalid contact

    except api_utils.APIError:
        return ""

async def send_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the send order conversation."""
    logger.info(f"send_command called by user {utils.get_account_id(update)}")

    if not await utils.is_authorized(update):
        logger.warning(f"Unauthorized access attempt by user {utils.get_account_id(update)}")
        await utils.send_unauthorized(update)
        return ConversationHandler.END

    # Check if command has arguments (amount and contact)
    args = context.args
    if args and len(args) >= 2:
        return await _handle_direct_command(update, context)

    # Show tier selection for interactive flow
    return await _show_tier_selection(update)

async def _handle_direct_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle /send <amount> <contact> command."""
    logger.info("Processing direct send command with parameters")

    try:
        amount = float(context.args[0])
        contact_input = ' '.join(context.args[1:])

        # Find nearest tier
        nearest_tier = find_nearest_tier(amount)
        if nearest_tier <= 0:
            await utils.send_message(update, config.MESSAGES["send_invalid_amount"])
            return ConversationHandler.END

        # Validate and get contact info
        account_id = utils.get_account_id(update)
        phone_number = validate_and_get_contact_info(contact_input, account_id)

        if phone_number == "":
            await utils.send_message(
                update,
                "❌ رقم الهاتف المدخل غير صحيح" if contact_input.isdigit() else
                f"❌ جهة الاتصال '{contact_input}' غير موجودة في قائمة جهات الاتصال الخاصة بك."
            )
            return ConversationHandler.END

        context.user_data.update({
            'tier': nearest_tier,
            'phone': phone_number
        })

        # Show confirmation
        return await show_confirmation(update, context)

    except ValueError:
        await utils.send_message(update, config.MESSAGES["send_invalid_amount_format"])
        return ConversationHandler.END
    except api_utils.APIError as e:
        logger.error(f"Error checking contacts: {e}")
        await utils.send_message(update, "❌ خطأ في الاتصال بالخادم. يرجى المحاولة لاحقاً.")
        return ConversationHandler.END

async def _show_tier_selection(update: Update) -> int:
    """Show tier selection keyboard."""
    logger.info("User authorized, showing tier selection")

    keyboard = []
    for tier in config.POPULAR_TIERS:
        keyboard.append([InlineKeyboardButton(f"{tier}", callback_data=f"tier_{tier}")])

    keyboard.append([InlineKeyboardButton(config.MESSAGES["send_custom_amount"], callback_data="custom_amount")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await utils.send_message(update, config.MESSAGES["send_select_tier"], reply_markup=reply_markup)
    return TIER

async def tier_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle tier selection."""
    query = update.callback_query
    await query.answer()

    tier = query.data.replace("tier_", "")
    context.user_data['tier'] = float(tier)

    await utils.send_message(update, config.MESSAGES["send_enter_phone_or_contact"])
    return PHONE

async def handle_custom_amount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle custom amount input."""
    query = update.callback_query
    await query.answer()

    await utils.send_message(update, config.MESSAGES["send_enter_custom_amount"])
    return SEND_AMOUNT

async def process_custom_amount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Process the custom amount and find nearest tier."""
    try:
        amount = float(update.message.text)
        nearest_tier = find_nearest_tier(amount)

        if nearest_tier <= 0:
            await utils.send_message(update, config.MESSAGES["send_invalid_amount"])
            return TIER

        context.user_data['tier'] = nearest_tier
        await utils.send_message(update, config.MESSAGES["send_enter_phone_or_contact"])
        return PHONE

    except ValueError:
        await utils.send_message(update, config.MESSAGES["send_invalid_amount_format"])
        return TIER

async def phone_entered(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle contact input for contact name/phone number."""
    contact_input = update.message.text
    account_id = utils.get_account_id(update)

    # Validate and get contact info
    phone_number = validate_and_get_contact_info(contact_input, account_id)

    if phone_number == "":
        await utils.send_message(
            update,
            "❌ رقم الهاتف المدخل غير صحيح" if contact_input.isdigit() else
            f"❌ جهة الاتصال '{contact_input}' غير موجودة في قائمة جهات الاتصال الخاصة بك."
        )
        context.user_data.clear()
        return ConversationHandler.END

    context.user_data.update({
        'phone': phone_number
    })

    return await show_confirmation(update, context)

async def show_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show confirmation message with transfer details."""
    tier = context.user_data.get('tier')
    phone = context.user_data.get('phone', 'غير محدد')

    confirmation_message = config.MESSAGES["send_confirmation"](tier, phone)

    keyboard = [
        [
            InlineKeyboardButton(config.MESSAGES["send_confirm_yes"], callback_data="confirm_yes"),
            InlineKeyboardButton(config.MESSAGES["send_confirm_no"], callback_data="confirm_no")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await utils.send_message(update, confirmation_message, reply_markup=reply_markup)
    return CONFIRM

async def confirm_request(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle request confirmation."""
    query = update.callback_query
    await query.answer()

    if query.data == "confirm_yes":
        # Prepare order data
        order_data = {
            "amount": context.user_data['tier'],
            "phone_number": context.user_data['phone']
        }

        try:
            account_id = utils.get_account_id(update)
            response = api_utils.create_request(account_id, order_data)
            await utils.send_message(update, config.MESSAGES["send_success"](response['request_id'], order_data['amount'], order_data['phone_number']))

        except api_utils.APIError as e:
            logger.error(f"Failed to create order: {e}")
            error_message = utils.format_api_error("ارسال تحويل جديد", e)
            await utils.send_message(update, error_message)
    else:
        await utils.send_message(update, config.MESSAGES["operation_canceled"])

    context.user_data.clear()
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel and end the conversation."""
    await utils.send_message(update, config.MESSAGES["operation_canceled"])
    context.user_data.clear()
    return ConversationHandler.END

# Create conversation handler
send_conv_handler = ConversationHandler(
    entry_points=[
        CommandHandler("send", send_command),
        CallbackQueryHandler(send_command, pattern='^send$')
    ],
    states={
        TIER: [
            CallbackQueryHandler(tier_selected, pattern=r"^tier_"),
            CallbackQueryHandler(handle_custom_amount, pattern="^custom_amount$")
        ],
        SEND_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_custom_amount)],
        PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, phone_entered)],
        CONFIRM: [CallbackQueryHandler(confirm_request, pattern=r"^confirm_")]
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)
