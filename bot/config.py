import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

# Telegram Bot Token from @BotFather
BOT_TOKEN = os.getenv('BOT_TOKEN', '')

# JWT Secret for token generation
JWT_SECRET = os.getenv('JWT_SECRET', '')

# JWT Expiration in days
JWT_EXPIRATION_DAYS = int(os.getenv('JWT_EXPIRATION_DAYS', 90))

# JWT Algorithm
JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')

# List of authorized user IDs (can be single user or multiple)
AUTHORIZED_USERS = [int(user_id.strip()) for user_id in os.getenv('AUTHORIZED_USERS', '').split(',') if user_id.strip().isdigit()]

# Dictionary to store authorized users and their JWT tokens (populated at startup by jwt_manager)
AUTHORIZED_TOKENS = {}

# Server configuration
SERVER_URL = os.getenv('SERVER_URL', 'https://your-production-server.com')

# Available tiers
TIERS = [45, 90, 180, 450, 900, 1800, 3600, 7200, 9000]

# Popular tiers to show as quick buttons
POPULAR_TIERS = [45, 90, 180, 450, 900]

# Max length of message
MAX_LEN = 2000

# Bot commands and descriptions
COMMANDS = {
    "start": "بدء البوت وعرض القائمة الرئيسية",
    "send": "تحويل جديد",
    "status": "التحقق من حالة الطلب",
    "tiers": "عرض الفئات المتاحة",
    "contact_add": "إضافة مستخدم جديد",
    "contact_delete": "حذف مستخدم",
    "contacts_get": "عرض قائمة المستخدمين"
}

# Messages
MESSAGES = {
    # General messages
    "welcome": lambda user_name: f"مرحباً {user_name}!\n\nلبدء استخدام البوت اختر من القائمة:",
    "unauthorized": "❌ عذراً، ليس لديك صلاحية استخدام هذا البوت.",
    "invalid_input": "⚠️ مدخل غير صحيح. الرجاء المحاولة مرة أخرى.",
    "operation_canceled": "❌ تم إلغاء العملية.",
    "server_error": "⚠️ حدث خطأ في الاتصال بالخادم. الرجاء المحاولة لاحقاً.",
    "config_error": "⚠️ حدث خطأ في إعدادات التطبيق. الرجاء مراجعة ملف الإعدادات.",
    
    # Send order messages
    "send_select_tier": "اختر القيمة المراد تحويلها",
    "send_custom_amount": "💰 إدخال مبلغ مخصص",
    "send_enter_phone_or_contact": "الرجاء إدخال رقم الهاتف أو جهة الاتصال:",
    "send_enter_custom_amount": "الرجاء إدخال المبلغ المطلوب:",
    "send_invalid_amount": "❌ المبلغ المدخل غير صحيح",
    "send_invalid_amount_format": "❌ الرجاء إدخال مبلغ صحيح",
    "send_invalid_phone": "⚠️ رقم الهاتف غير صالح. الرجاء إدخال رقم هاتف صحيح.",
    "send_confirmation": lambda tier, phone: (
        f"📋 تأكيد الطلب:\n"
        f"• المبلغ: {tier}\n"
        f"• رقم الهاتف: {phone}\n\n"
        "هل أنت متأكد من أنك تريد إجراء هذا التحويل؟"
    ),
    "send_confirm_yes": "✅ نعم",
    "send_confirm_no": "❌ لا",
    "send_success": lambda id, tier, phone: (f"✅ تم انشاء الطلب رقم {id} لتحويل {tier} لرقم {phone} بنجاح!"),
    "send_failed": "❌ فشل في إرسال الطلب. الرجاء المحاولة لاحقاً.",
    
    # Contact management messages
    "contact_add_prompt": "الرجاء إدخال رقم هاتف جهة الاتصال الجديدة:",
    "contact_add_success": lambda contact_id: f"✅ تمت إضافة جهة الاتصال '{contact_id}' بنجاح!",
    "contact_delete_prompt": "اختر جهة الاتصال التي تريد حذفها:",
    "contact_delete_success": lambda contact_name: f"✅ تم حذف جهة الاتصال '{contact_name}' بنجاح!",
    "contact_delete_not_found": "❌ جهة الاتصال غير موجودة.",
    "contact_no_contacts": "❌ لا يوجد جهات اتصال مسجلة.",
    "contact_add_button": "➕ إضافة جهة اتصال",
    "contact_delete_button_main": "🗑️ حذف جهة اتصال",
    "contact_cancel_button": "🔙 إلغاء",
    
    # Status check messages
    "status_enter_request_id": "الرجاء إدخال رقم الطلب:",
    "status_details": lambda request_id, status, amount, phone_number: (
        f"📋 تفاصيل الطلب #{request_id}\n"
        f"• الحالة: {status}\n"
        f"• المبلغ: {amount}\n"
        f"• رقم الهاتف: {phone_number}\n"
    ),
    "status_pending": "⏳ قيد الانتظار",
    "status_processing": "🔄 قيد المعالجة",
    "status_completed": "✅ مكتمل",
    "status_failed": "❌ فشل",
    "status_unknown": "غير معروف",
    "status_error": lambda error: f"⚠️ {error}",
    
    # Tiers messages
    "tiers_title": "📋 الفئات المتاحة:\n\n",
    "tiers_item": lambda tier: f"• {tier}\n",
    
    # Button labels
    "button_send": "✉️ تحويل جديد",
    "button_status": "📦 حالة الطلب",
    "button_tiers": "📋 الفئات المتاحة",
    "button_contacts_get": "👥 عرض جهات الاتصال",
}

# Validate required configurations
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set in environment variables")
if not AUTHORIZED_USERS:
    raise ValueError("AUTHORIZED_USERS is not properly configured in environment variables")
if not JWT_SECRET:
    raise ValueError("JWT_SECRET is not set in environment variables")
