from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ConversationHandler
from . import api_utils
from . import utils
import config
import logging

logger = logging.getLogger(__name__)

# Conversation state
REQUEST_ID = 0

status_map = {
    "Pending": config.MESSAGES["status_pending"],
    "Processing": config.MESSAGES["status_processing"],
    "Completed": config.MESSAGES["status_completed"],
    "Failed": config.MESSAGES["status_failed"]
}

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the status check conversation."""
    if not await utils.is_authorized(update):
        await utils.send_unauthorized(update)
        return ConversationHandler.END
    
    # Check if request ID was provided with the command
    if context.args:
        request_id = ' '.join(context.args)
        await check_request_status(update, context, request_id)
        return ConversationHandler.END

    
    # If no request ID provided, ask for it
    await utils.send_message(update, config.MESSAGES["status_enter_request_id"])
    return REQUEST_ID

async def get_request_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Get request ID from user input."""
    request_id = update.message.text.strip()
    await check_request_status(update, context, request_id)
    return ConversationHandler.END

async def check_request_status(update: Update, context: ContextTypes.DEFAULT_TYPE, request_id: str) -> int:
    """Check the status of a request."""
    try:
        # Get account_id for this user
        account_id = utils.get_account_id(update)
        
        # Make API call to get request status
        response_data = api_utils.get_request_status(account_id, request_id)
        
        # If the API returns data in a 'data' field, use that
        if 'data' in response_data:
            response_data = response_data['data']
            
        # Ensure required fields have default values
        response_data.setdefault('status', 'unknown')
        response_data.setdefault('amount', 'غير معروف')
        response_data.setdefault('phone_number', 'غير متوفر')
        response_data['request_id'] = request_id
        
        status = status_map.get(response_data.get("status", ""), config.MESSAGES["status_unknown"])
        
        message = config.MESSAGES["status_details"](
            request_id,
            status,
            response_data.get('amount', 'غير متوفر'),
            response_data.get('phone_number', 'غير متوفر')
        )
        
        await utils.send_message(update, message)
            
    except api_utils.APIError as e:
        logger.error(f"API Error checking status: {e}")
        
        # Handle specific status codes
        if hasattr(e, 'status_code') and e.status_code == 404:
            error_message = f"❌ الطلب {request_id} غير موجود."
        else:
            error_message = utils.format_api_error("التحقق من حالة الطلب", e)
        
        await utils.send_message(update, error_message)
    except Exception as e:
        logger.error(f"Unexpected error checking status: {e}")
        await utils.send_message(update, config.MESSAGES["server_error"])
    

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel and end the conversation."""
    await utils.send_message(update, config.MESSAGES["operation_canceled"])
    return ConversationHandler.END

# Create conversation handler
status_conv_handler = ConversationHandler(
    entry_points=[
        CommandHandler("status", status_command),
        CallbackQueryHandler(status_command, pattern='^status$'),
        MessageHandler(filters.Regex(r'^/status\s+\d+$'), status_command)
    ],
    states={
        REQUEST_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_request_id)]
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)
