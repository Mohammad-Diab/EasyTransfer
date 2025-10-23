"""
Application constants and error messages
"""

# Error Messages - Requests

ERROR_MISSING_REQUIRED_FIELDS_REQUEST = "الحقول phone_number و amount مطلوبة"
ERROR_INVALID_STATUS = "الحالة يجب أن تكون Success أو Failed"
ERROR_REQUEST_NOT_FOUND = "الطلب غير موجود"

# Error Messages - Contacts
ERROR_MISSING_REQUIRED_FIELDS_CONTACT = "رقم الهاتف والاسم مطلوبان"
ERROR_CONTACT_LIMIT_REACHED = "تم الوصول للحد الأقصى. الحد الأقصى {limit} جهات اتصال لكل حساب"
ERROR_DUPLICATE_CONTACT_NAME = "جهة الاتصال بالاسم '{name}' موجودة بالفعل"
ERROR_PHONE_NUMBER_TOO_LONG = "رقم الهاتف يجب أن يكون 14 حرف أو أقل"
ERROR_NAME_TOO_LONG = "الاسم يجب أن يكون 50 حرف أو أقل"
ERROR_NAME_IS_DIGIT = "الاسم يجب أن يحتوي على حروف"
ERROR_CONTACT_NOT_FOUND = "جهة الاتصال غير موجودة"
ERROR_CONTACT_PERMISSION_DENIED = "يمكنك فقط حذف جهات الاتصال الخاصة بك"

# Success Messages
SUCCESS_CONTACT_ADDED = "تمت إضافة جهة الاتصال بنجاح"
SUCCESS_CONTACT_DELETED = "تم حذف جهة الاتصال بنجاح"

# Status Messages
STATUS_PONG = "pong"
STATUS_OK = "ok"
STATUS_EMPTY = "empty"
STATUS_PENDING = "Pending"
STATUS_PROCESSING = "Processing"
STATUS_DONE = "Done"
STATUS_FAILED = "Failed"
STATUS_SUCCESS = "Success"
MESSAGE_NO_PENDING_REQUESTS = "لا توجد طلبات معلقة"

# JWT Authentication Error Messages
ERROR_TOKEN_NOT_PROVIDED = "رمز المصادقة مطلوب"
ERROR_INVALID_TOKEN = "رمز المصادقة غير صالح أو منتهي الصلاحية"

# Validation Constants
MAX_PHONE_NUMBER_LENGTH = 14
MAX_NAME_LENGTH = 50
