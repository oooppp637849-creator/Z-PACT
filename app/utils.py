# ================================================================
# app/utils.py — أدوات مساعدة عامة (Sanitization & Helpers)
# ================================================================

import re
from typing import Optional

def sanitize_string(text: Optional[str]) -> Optional[str]:
    """
    تطهير النصوص من أي وسوم HTML أو أكواد خبيثة (XSS Protection).
    يقوم بإزالة أي شيء بين < > لضمان عدم وجود h1, script, etc.
    """
    if text is None:
        return None
    
    # 1. إزالة وسوم HTML بالكامل
    clean_text = re.sub(r'<[^>]*>', '', text)
    
    # 2. تنظيف المسافات الزائدة في البداية والنهاية
    clean_text = clean_text.strip()
    
    return clean_text

def sanitize_phone(phone: Optional[str]) -> Optional[str]:
    """تنظيف أرقام الهواتف من أي مسافات أو رموز غير رقمية"""
    if not phone:
        return phone
    return re.sub(r'[^\d+]', '', phone)
