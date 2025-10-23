from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackQueryHandler
import config
import logging
from . import utils, api_utils

logger = logging.getLogger(__name__)

# Conversation states
CONTACT_ADD_PHONE, CONTACT_ADD_NAME, CONTACT_DELETE = range(3)

async def contact_add_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the add contact conversation."""
    if not await utils.is_authorized(update):
        await utils.send_unauthorized(update)
        return ConversationHandler.END
    
    await utils.send_message(update, config.MESSAGES["contact_add_prompt"])
    return CONTACT_ADD_PHONE

async def add_contact_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Get phone number for new contact."""
    phone_number = update.message.text.strip()
    
    # Validate phone number
    if not phone_number.isdigit() or len(phone_number) < 10:
        await utils.send_message(update, config.MESSAGES["send_invalid_phone"])
        return CONTACT_ADD_PHONE
    
    # Store phone in context
    context.user_data['contact_phone'] = phone_number
    await utils.send_message(update, "الرجاء إدخال اسم جهة الاتصال:")
    return CONTACT_ADD_NAME

async def add_contact_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Add contact with name and phone."""
    name = update.message.text.strip()
    phone_number = context.user_data.get('contact_phone')
    
    try:
        # Get account_id for this user
        account_id = utils.get_account_id(update)
        
        # Add contact via API
        response = api_utils.add_contact(account_id, phone_number, name)
        await utils.send_message(update, config.MESSAGES["contact_add_success"](name))
        
    except api_utils.APIError as e:
        logger.error(f"Failed to add contact: {e}")
        error_message = utils.format_api_error("إضافة جهة الاتصال", e)
        await utils.send_message(update, error_message)
    
    # Clear context
    context.user_data.clear()
    return ConversationHandler.END

async def contact_delete_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the delete contact conversation."""
    if not await utils.is_authorized(update):
        await utils.send_unauthorized(update)
        return ConversationHandler.END
    
    try:
        # Get account_id for this user
        account_id = utils.get_account_id(update)
        
        # Get contacts from API
        response = api_utils.get_contacts(account_id)
        contacts = response.get('data', response.get('contacts', []))
        
        if not contacts:
            await utils.send_message(update, config.MESSAGES["contact_no_contacts"])
            return ConversationHandler.END
        
        # Create a list of contacts to delete
        keyboard = []
        for contact in contacts:
            contact_id = contact.get('id')
            contact_name = contact.get('name', contact.get('phone_number', 'Unknown'))
            keyboard.append([
                InlineKeyboardButton(
                    f"❌ {contact_name} (ID: {contact_id})", 
                    callback_data=f"delete_{contact_id}_{contact_name}"
                )
            ])
    except api_utils.APIError as e:
        logger.error(f"Failed to get contacts: {e}")
        error_message = utils.format_api_error("جلب قائمة جهات الاتصال", e)
        await utils.send_message(update, error_message)
        return ConversationHandler.END
    
    keyboard.append([InlineKeyboardButton(config.MESSAGES["contact_cancel_button"], callback_data="cancel")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await utils.send_message(update, config.MESSAGES["contact_delete_prompt"], reply_markup=reply_markup)
    return CONTACT_DELETE

async def delete_contact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Delete a contact."""
    query = update.callback_query
    await query.answer()
    
    if query.data == "cancel":
        await utils.send_message(query, config.MESSAGES["operation_canceled"])
        return ConversationHandler.END
    
    contact_id, contact_name = query.data.replace("delete_", "").split("_")
    
    try:
        # Get account_id for this user
        account_id = utils.get_account_id(update)
        
        # Delete contact via API
        response = api_utils.delete_contact(account_id, contact_id)
        await utils.send_message(query, config.MESSAGES["contact_delete_success"](contact_name))
        
    except api_utils.APIError as e:
        logger.error(f"Failed to delete contact: {e}")
        
        # Check if it's a 404 error
        if hasattr(e, 'status_code') and e.status_code == 404:
            error_message = config.MESSAGES["contact_delete_not_found"]
        else:
            error_message = utils.format_api_error("حذف جهة الاتصال", e)
        
        await utils.send_message(query, error_message)
    
    return ConversationHandler.END

async def contacts_get_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show list of all contacts."""
    if not await utils.is_authorized(update):
        await utils.send_unauthorized(update)
        return
    
    try:
        # Get account_id for this user
        account_id = utils.get_account_id(update)
        
        # Get contacts from API
        response = api_utils.get_contacts(account_id)
        contacts = response.get('data', response.get('contacts', []))
        
        if not contacts:
            await utils.send_message(update, config.MESSAGES["contact_no_contacts"])
            return
        
        message = "📞 قائمة جهات الاتصال:\n\n"
        for contact in contacts:
            contact_id = contact.get('id')
            contact_name = contact.get('name', 'N/A')
            phone_number = contact.get('phone_number', 'N/A')
            message += f"• (Id: {contact_id}): {contact_name} - {phone_number}\n"
    
    except api_utils.APIError as e:
        logger.error(f"Failed to get contacts: {e}")
        error_message = utils.format_api_error("جلب قائمة جهات الاتصال", e)
        await utils.send_message(update, error_message)
        return
    
    await utils.send_message(update, message)

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel and end the conversation."""
    await utils.send_message(update, config.MESSAGES["operation_canceled"])
    return ConversationHandler.END

# Create conversation handlers
add_contact_conv_handler = ConversationHandler(
    entry_points=[
        CommandHandler("contact_add", contact_add_command),
        CallbackQueryHandler(contact_add_command, pattern='^contact_add$')
    ],
    states={
        CONTACT_ADD_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_contact_phone)],
        CONTACT_ADD_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_contact_name)]
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)

delete_contact_conv_handler = ConversationHandler(
    entry_points=[
        CommandHandler("contact_delete", contact_delete_command),
        CallbackQueryHandler(contact_delete_command, pattern='^contact_delete$')
    ],
    states={
        CONTACT_DELETE: [CallbackQueryHandler(delete_contact, pattern=r"^delete_|^cancel$")]
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)

# Handler for the contacts command
contacts_get_handler = CommandHandler("contacts_get", contacts_get_command)
contacts_get_callback_handler = CallbackQueryHandler(contacts_get_command, pattern='^contacts_get$')
