import os
import sys

# Add the root directory to the python path so imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import ChatMessage
import bleach
from datetime import datetime, timedelta

def clean_all_chat_messages():
    db = SessionLocal()
    try:
        now = datetime.utcnow()
        retention_period = timedelta(days=30)  # الاحتفاظ بالرسائل لمدة 30 يوم
        cutoff_date = now - retention_period

        # 1. حذف الرسائل الأقدم من 30 يوماً فقط
        deleted_count = db.query(ChatMessage).filter(ChatMessage.created_at < cutoff_date).delete()
        
        # 2. فحص أحدث 100 رسالة فقط للتأكد من خلوها من وسوم HTML الخبيثة
        recent_messages = db.query(ChatMessage).order_by(ChatMessage.created_at.desc()).limit(100).all()
        cleaned_count = 0
        for msg in recent_messages:
            if not msg.message:
                continue
            clean_text = bleach.clean(msg.message, tags=[], strip=True)
            if clean_text != msg.message:
                if clean_text.strip():
                    msg.message = clean_text
                    cleaned_count += 1

        db.commit()
        if deleted_count > 0 or cleaned_count > 0:
            print(f"Cleanup complete. Sanitized {cleaned_count} messages. Deleted {deleted_count} expired messages.")
    except Exception as e:
        print(f"Chat cleanup error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    clean_all_chat_messages()
