# ================================================================
# app/worker.py — عامل النظافة والصيانة (Cleanup Worker)
# ================================================================

import asyncio
import os
import time
import shutil
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app import models, database
from app.config import settings

from app.logger import logger

# مسار تخزين الملفات المختومة المرفوعة (المسار المطلق)
STAMPED_DIR = os.path.join(settings.STORAGE_DIR, "stamped")

async def start_cleanup_worker():
    """
    مهمة خلفية تعمل دورياً لتنظيف النظام من الملفات والتوكنات القديمة.
    """
    logger.info("🧹 [Worker] Cleanup worker started.")
    
    while True:
        try:
            # 1. تنظيف الملفات المختومة (أقدم من 24 ساعة)
            clean_stamped_files()
            
            # 2. تنظيف قاعدة البيانات من التوكنات المنتهية
            clean_expired_tokens()
            
            # 3. تنظيف توكنات التحميل في الذاكرة (Purchases)
            from app.routers.purchases import _download_tokens
            clean_memory_tokens(_download_tokens)
            
        except Exception as e:
            logger.error(f"⚠️ [Worker Error] {e}")
            
        # الانتظار لمدة ساعة قبل الدورة القادمة
        await asyncio.sleep(3600)

def clean_stamped_files():
    """حذف الملفات من المجلد المؤقت التي مر عليها أكثر من 7 أيام (168 ساعة)"""
    if not os.path.exists(STAMPED_DIR):
        return
        
    now = time.time()
    count = 0
    # الاحتفاظ بالملفات لمدة 7 أيام لضمان عدم ضياعها على المشتري
    retention_period = 7 * 24 * 3600 
    
    for filename in os.listdir(STAMPED_DIR):
        file_path = os.path.join(STAMPED_DIR, filename)
        # إذا كان الملف أقدم من المدة المحددة
        if os.path.getmtime(file_path) < now - retention_period:
            try:
                os.remove(file_path)
                count += 1
            except:
                pass
    if count > 0:
        logger.info(f"🧹 [Worker] Deleted {count} old stamped files (older than 7 days).")

def clean_expired_tokens():
    """حذف توكنات المعاينة المنتهية من قاعدة البيانات"""
    db = database.SessionLocal()
    try:
        now = datetime.utcnow()
        deleted = db.query(models.PreviewToken).filter(models.PreviewToken.expires_at < now).delete()
        db.commit()
        if deleted > 0:
            logger.info(f"🧹 [Worker] Removed {deleted} expired preview tokens from DB.")
    finally:
        db.close()

def clean_memory_tokens(tokens_dict: dict):
    """تنظيف توكنات التحميل المخزنة في الذاكرة بأمان"""
    now = datetime.utcnow()
    to_delete = []
    for token, data in list(tokens_dict.items()):
        if data.get("expires_at") and data.get("expires_at") < now:
            to_delete.append(token)
            
    for token in to_delete:
        tokens_dict.pop(token, None)
    
    if len(to_delete) > 0:
        logger.info(f"🧹 [Worker] Cleared {len(to_delete)} expired download tokens from memory.")
