# ================================================================
# app/database.py — إعداد الاتصال بقاعدة البيانات
#
# المسؤوليات:
#   - إنشاء engine الاتصال بـ SQLite
#   - تعريف SessionLocal لإدارة جلسات قاعدة البيانات
#   - توفير get_db() كـ dependency في FastAPI
# ================================================================

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sqlite3
import os

from app.models import Base
from app.config import settings
from app.logger import logger

# -----------------------------------------------------------
# استخدام المسار المطلق المحسوب في الإعدادات
# -----------------------------------------------------------
DATABASE_URL = settings.DATABASE_URL

# إذا كان SQLite، نستخدم المسار المطلق لضمان الثبات
if "sqlite" in DATABASE_URL:
    db_path = settings.DATABASE_PATH
    # التأكد من وجود المجلد الخاص بقاعدة البيانات
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    DATABASE_URL = f"sqlite:///{db_path}"

# -----------------------------------------------------------
# الـ Engine — نقطة الاتصال بقاعدة البيانات مع إعدادات الأداء الخارق
# -----------------------------------------------------------
connect_args = {
    "check_same_thread": False,
    "timeout": 60.0, # ينتظر حتى 60 ثانية لإنهاء عمليات الكتابة دون إلقاء خطأ database is locked
} if "sqlite" in DATABASE_URL else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    echo=False,
    pool_pre_ping=True,
)

# تفعيل إعدادات الأداء الأقصى (WAL Mode + Memory Cache + MMAP) لتحمل 100,000 مستخدم
if "sqlite" in DATABASE_URL:
    from sqlalchemy import event
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA busy_timeout=60000") # 60 ثانية انتظار لتفادي الـ Lock
        cursor.execute("PRAGMA cache_size=-64000") # كاش 64 ميجابايت في الرام لكل اتصال
        cursor.execute("PRAGMA temp_store=MEMORY") # حفظ الجداول والفهارس المؤقتة بالكامل في الرام
        cursor.execute("PRAGMA mmap_size=2147483648") # 2 جيجابايت Memory-Mapped I/O لسرعة قراءة فورية من الرام
        cursor.close()

# -----------------------------------------------------------
# SessionLocal — Factory لإنشاء جلسات قاعدة البيانات
# autocommit=False: لازم نعمل commit يدوي بعد كل تغيير
# autoflush=False:  منعمل flush تلقائي للـ session
# -----------------------------------------------------------
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)


def patch_database_schema():
    """
    دالة ترقيع قاعدة البيانات — تقوم بإضافة الأعمدة الناقصة للجداول الحالية
    دون المساس بالبيانات الموجودة.
    """
    if "sqlite" not in DATABASE_URL:
        return
        
    db_path = settings.DATABASE_PATH
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 1. قائمة بالأعمدة المراد إضافتها لجدول users
        # الصيغة: (الجدول، العمود، نوع البيانات)
        columns_to_add = [
            ("users", "referral_code", "TEXT"),
            ("users", "referred_by_id", "INTEGER"),
            ("users", "referral_reward_claimed", "BOOLEAN DEFAULT 0"),
            ("materials", "page_frame_path", "TEXT"),
            ("users", "watermark_logo_path", "TEXT"),
            ("users", "preferences", "JSON"),
            ("purchases", "watermark_type", "TEXT DEFAULT 'text'"),
            ("purchases", "buyer_phone_stamp_2", "TEXT"),
            ("chat_messages", "reply_to_id", "INTEGER"),
        ]
        
        for table, column, col_type in columns_to_add:
            try:
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}")
                logger.info(f"✓ [Patch] Added column {column} to table {table}")
            except sqlite3.OperationalError as e:
                # إذا كان العمود موجوداً بالفعل سيظهر خطأ، نقوم بتجاهله
                if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
                    pass
                else:
                    logger.warning(f"⚠️ [Patch Warning] Could not add column {column}: {e}")
        
        # 2. إنشاء فهارس السرعة الفائقة لقاعدة البيانات لتسريع الاستعلامات 10 أضعاف
        indexes_to_create = [
            "CREATE INDEX IF NOT EXISTS idx_materials_published_created ON materials(is_published, created_at DESC)",
            "CREATE INDEX IF NOT EXISTS idx_materials_uploader ON materials(uploaded_by)",
            "CREATE INDEX IF NOT EXISTS idx_purchases_buyer_status ON purchases(buyer_id, status)",
            "CREATE INDEX IF NOT EXISTS idx_purchases_material ON purchases(material_id)",
            "CREATE INDEX IF NOT EXISTS idx_purchases_created ON purchases(purchased_at DESC)",
            "CREATE INDEX IF NOT EXISTS idx_chat_messages_created ON chat_messages(created_at DESC)",
            "CREATE INDEX IF NOT EXISTS idx_notifications_user_read ON notifications(user_id, is_read)",
            "CREATE INDEX IF NOT EXISTS idx_wallet_tx_phone_amount ON wallet_transactions(sender_phone, amount)",
            "CREATE INDEX IF NOT EXISTS idx_coin_tx_user_created ON coin_transactions(user_id, created_at DESC)",
            "CREATE INDEX IF NOT EXISTS idx_user_devices_lookup ON user_devices(user_id, device_id)",
        ]
        for idx_sql in indexes_to_create:
            try:
                cursor.execute(idx_sql)
            except Exception as e:
                logger.warning(f"⚠️ [Index Warning] {e}")

        conn.commit()
        conn.close()
        logger.info("✓ [Patch] Database schema and performance indexes synced successfully")
        
    except Exception as e:
        logger.error(f"❌ [Patch Error] Unexpected error during database patch: {e}")


def sync_external_database():
    """
    دمج البيانات من قاعدة بيانات خارجية (seed.db) إلى قاعدة البيانات الأساسية.
    تُستخدم هذه الدالة لإضافة المذكرات والمستخدمين والتنسيقات الجاهزة دون مسح البيانات الحالية.
    """
    if "sqlite" not in DATABASE_URL:
        return

    main_db_path = settings.DATABASE_PATH
    # نبحث عن ملف باسم seed.db في المسار الرئيسي للمشروع
    seed_db_path = os.path.join(settings.BASE_DIR, "seed.db")

    if not os.path.exists(seed_db_path):
        # logger.info("ℹ️ [Sync] No seed.db found, skipping sync.")
        return

    logger.info(f"🚀 [Sync] Found seed.db, starting smart merge into {main_db_path}...")
    
    try:
        conn = sqlite3.connect(main_db_path)
        cursor = conn.cursor()
        
        # ربط قاعدة البيانات الخارجية (seed.db) بالاتصال الحالي
        cursor.execute(f"ATTACH DATABASE '{seed_db_path}' AS source")
        
        # قائمة الجداول التي نريد دمجها (الترتيب مهم بسبب العلاقات)
        tables_to_sync = [
            "users", 
            "materials", 
            "stamp_layouts", 
            "layout_presets", 
            "spending_levels", 
            "blacklist"
        ]
        
        for table in tables_to_sync:
            try:
                # التحقق من عدد السجلات للمقارنة الذكية
                cursor.execute(f"SELECT count(*) FROM main.{table}")
                main_count = cursor.fetchone()[0]
                
                cursor.execute(f"SELECT count(*) FROM source.{table}")
                source_count = cursor.fetchone()[0]
                
                if source_count > 0:
                    # دمج السجلات التي لا تملك ID مكرر (INSERT OR IGNORE)
                    # هذا يضمن أننا نأخذ البيانات الجديدة ونترك البيانات الحالية كما هي
                    cursor.execute(f"INSERT OR IGNORE INTO main.{table} SELECT * FROM source.{table}")
                    
                    # التحقق من عدد السجلات الجديد لمعرفة كم سجل تمت إضافته
                    cursor.execute(f"SELECT count(*) FROM main.{table}")
                    final_count = cursor.fetchone()[0]
                    added_count = final_count - main_count
                    
                    if added_count > 0:
                        logger.info(f"✅ [Sync] Table '{table}': Merged {added_count} new records (Source: {source_count}, Total now: {final_count})")
                    else:
                        logger.info(f"ℹ️ [Sync] Table '{table}': No new records to merge.")
                
            except sqlite3.OperationalError as e:
                logger.warning(f"⚠️ [Sync Warning] Could not sync table {table}: {e}")
        
        cursor.execute("DETACH DATABASE source")
        conn.commit()
        conn.close()
        logger.info("🏁 [Sync] Smart database merge completed.")

    except Exception as e:
        logger.error(f"❌ [Sync Error] Failed to sync external database: {e}")


def create_tables():
    """
    إنشاء كل الجداول في قاعدة البيانات لو مش موجودة.
    بيُنفَّذ مرة واحدة عند بدء تشغيل التطبيق.
    تلقائياً يقوم بإنشاء حساب مدير افتراضي (Admin) إذا كانت قاعدة البيانات فارغة.
    """
    # 1. الترقيع للأعمدة الجديدة في الجداول القديمة
    patch_database_schema()
    
    # 2. إنشاء الجداول الجديدة (مثل user_devices) مع حماية ضد تداخل الـ Workers المتزامنة
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        logger.warning(f"ملاحظة أثناء إنشاء الجداول (قد يكون worker آخر قام بإنشائها): {e}")

    # 3. دمج البيانات الخارجية لو وجدت (Smart Merge)
    sync_external_database()
    
    # -----------------------------------------------------------
    # Seed تلقائي لحساب المدير لسهولة التشغيل في بيئة الإنتاج الفعلي
    # -----------------------------------------------------------
    db = SessionLocal()
    try:
        from app.models import User, UserRole
        from app.crud import hash_password

        # التحقق إذا كان هناك أي حساب مدير موجود مسبقاً
        existing_admin = db.query(User).filter(User.role == UserRole.ADMIN).first()
        if not existing_admin:
            new_admin = User(
                full_name="مصطفى (المدير)",
                email="admin@elite.com",
                password_hash=hash_password("admin123456"), # يمكنك تغييرها لاحقاً من لوحة التحكم
                role=UserRole.ADMIN,
                is_active=True,
                coins=0.0
            )
            db.add(new_admin)
            db.commit()
            logger.info("[AUTO-SEED] Created default admin user: admin@elite.com / admin123456")
    except Exception as e:
        # لا نوقف تشغيل التطبيق لو حصل مشكلة بالـ seed لضمان استمرارية الخدمة
        logger.error(f"[AUTO-SEED] Error seeding default admin: {e}")
    finally:
        db.close()



def get_db():
    """
    FastAPI Dependency — بتعطي كل Request جلسة DB منفصلة
    وبتضمن إغلاقها بعد انتهاء الـ Request حتى لو حصل error.

    الاستخدام في FastAPI endpoint:
        @app.get("/example")
        def example(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db          # بيعطي الـ session للـ endpoint
    finally:
        db.close()        # بيُغلق الـ session دايماً في الآخر
