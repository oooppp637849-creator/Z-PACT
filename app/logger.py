# ================================================================
# app/logger.py — نظام الـ Logging المركزي والمحمي للمشروع
# ================================================================

import logging
import os
from logging.handlers import RotatingFileHandler
from app.config import settings

# مسار ملف السجلات في المجلد الرئيسي للمشروع
log_file_path = os.path.join(settings.BASE_DIR, "app.log")

# إنشاء الـ Logger المركزي
logger = logging.getLogger("webpdf_elite")
logger.setLevel(logging.INFO)

# تنسيق السجلات ليكون احترافياً ومقروءاً مع التاريخ ومستوى الخطورة والملف المصدر
log_formatter = logging.Formatter(
    "%(asctime)s [%(levelname)s] (%(name)s) - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# 1. تخديم السجلات على الـ Terminal (Console)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(log_formatter)

# 2. تخديم السجلات وحفظها في ملف دوار (Rotating File) لمنع تضخم المساحة
file_handler = RotatingFileHandler(
    log_file_path,
    maxBytes=10 * 1024 * 1024,  # 10 ميجابايت للملف الواحد كحد أقصى
    backupCount=5,               # أرشفة حتى 5 ملفات قديمة
    encoding="utf-8"
)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(log_formatter)

# ربط الموزعين بالـ Logger
if not logger.handlers:
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
