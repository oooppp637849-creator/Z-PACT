# ================================================================
# app/crud.py — عمليات قاعدة البيانات (Create, Read, Update, Delete)
#
# كل دالة هنا مسؤولة عن عملية واحدة فقط على قاعدة البيانات.
# الـ endpoints في routers/ بتستدعي الدوال دي — مش بتتكلم
# مع قاعدة البيانات مباشرة. ده بيخلي الكود نظيف وسهل الاختبار.
#
# التنظيم:
#   crud_user      → عمليات المستخدمين
#   crud_material  → عمليات الملفات
#   crud_layout    → عمليات تنسيقات الأختام
#   crud_purchase  → عمليات المشتريات
#   crud_token     → عمليات توكنات المعاينة
# ================================================================

import secrets
import uuid
from datetime import datetime, timedelta
from typing import Optional

import bcrypt
from sqlalchemy.orm import Session, joinedload

from app import models, schemas

# -----------------------------------------------------------
# تشفير كلمات المرور باستخدام مكتبة bcrypt مباشرة لحل مشاكل توافق passlib
# -----------------------------------------------------------

def hash_password(password: str) -> str:
    """تشفير كلمة المرور — بنخزن الـ hash مش الكلمة الأصلية أبداً"""
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_bytes = bcrypt.hashpw(pwd_bytes, salt)
    return hashed_bytes.decode('utf-8')


def verify_password(plain: str, hashed: str) -> bool:
    """التحقق من كلمة المرور مقارنةً بالـ hash المخزن"""
    try:
        return bcrypt.checkpw(plain.encode('utf-8'), hashed.encode('utf-8'))
    except Exception:
        return False



# ================================================================
# CRUD — USERS
# ================================================================

def get_user_by_id(db: Session, user_id: int) -> Optional[models.User]:
    """جلب مستخدم بالـ ID"""
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    """جلب مستخدم بالإيميل — بيُستخدم في تسجيل الدخول"""
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(
    db:   Session,
    data: schemas.UserCreate,
    role: models.UserRole = models.UserRole.CUSTOMER,
) -> models.User:
    """
    إنشاء مستخدم جديد.
    الـ role بيتحدد من الـ Backend — مش من الـ Client.
    """
    # توليد كود دعوة فريد
    import secrets
    ref_code = secrets.token_hex(4).upper() # 8 characters
    
    user = models.User(
        full_name     = data.full_name,
        email         = data.email,
        password_hash = hash_password(data.password),
        role          = role,
        referral_code = ref_code,
        referred_by_id = None
    )
    
    # لو فيه كود دعوة، نربطه
    if data.referral_code:
        inviter = db.query(models.User).filter(models.User.referral_code == data.referral_code).first()
        if inviter:
            user.referred_by_id = inviter.id

    db.add(user)
    db.commit()
    db.refresh(user)  # بنجيب الـ id اللي اتعمله من قاعدة البيانات
    return user


def authenticate_user(db: Session, email: str, password: str) -> Optional[models.User]:
    """
    التحقق من بيانات الدخول.
    بيرجع الـ User لو صح، أو None لو غلط.
    """
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    if not user.is_active:
        return None
    return user


def deactivate_user(db: Session, user_id: int) -> Optional[models.User]:
    """إيقاف حساب مستخدم (بدل الحذف الكامل للحفاظ على سجل المشتريات)"""
    user = get_user_by_id(db, user_id)
    if not user:
        return None
    user.is_active = False
    db.commit()
    db.refresh(user)
    return user


def get_all_users(
    db:    Session,
    skip:  int = 0,
    limit: int = 100,
    search: str = None,
) -> tuple[list[models.User], int]:
    """جلب كل المستخدمين (للـ Admin) مع إمكانية البحث"""
    query = db.query(models.User)
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (models.User.full_name.ilike(search_filter)) |
            (models.User.email.ilike(search_filter)) |
            (models.User.id.cast(models.String).ilike(search_filter))
        )
    query = query.order_by(models.User.created_at.desc())
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return items, total


# ================================================================
# DEVICE MANAGEMENT
# ================================================================

def get_user_devices(db: Session, user_id: int):
    return db.query(models.UserDevice).filter(models.UserDevice.user_id == user_id).all()

def register_user_device(db: Session, user_id: int, device_id: str, user_agent: str = None, ip: str = None):
    # Check if already exists
    device = db.query(models.UserDevice).filter(
        models.UserDevice.user_id == user_id,
        models.UserDevice.device_id == device_id
    ).first()
    
    if device:
        device.last_login = datetime.utcnow()
        device.last_ip = ip
        device.user_agent = user_agent
        db.commit()
        return device
    
    # Create new
    device = models.UserDevice(
        user_id=user_id,
        device_id=device_id,
        user_agent=user_agent,
        last_ip=ip
    )
    db.add(device)
    db.commit()
    db.refresh(device)
    return device

def delete_all_user_devices(db: Session, user_id: int):
    """حذف كل الأجهزة المسجلة للمستخدم (Reset)"""
    db.query(models.UserDevice).filter(models.UserDevice.user_id == user_id).delete()
    db.commit()

# ================================================================
# BLACKLIST OPERATIONS
# ================================================================

def add_to_blacklist(db: Session, val_type: str, value: str, reason: str = None):
    # Check if exists
    existing = db.query(models.Blacklist).filter(models.Blacklist.value == value).first()
    if existing: return existing
    
    entry = models.Blacklist(type=val_type, value=value, reason=reason)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry

def get_blacklist(db: Session):
    return db.query(models.Blacklist).order_by(models.Blacklist.created_at.desc()).all()

def remove_from_blacklist(db: Session, entry_id: int):
    db.query(models.Blacklist).filter(models.Blacklist.id == entry_id).delete()
    db.commit()

def is_blacklisted(db: Session, value: str) -> bool:
    if not value: return False
    return db.query(models.Blacklist).filter(models.Blacklist.value == value).first() is not None

def check_stamp_data_against_blacklist(db: Session, name: str, phone: str, text: str):
    """التحقق من البيانات المدخلة للختم ضد القائمة السوداء"""
    if is_blacklisted(db, phone): return f"⚠️ رقم الهاتف '{phone}' محظور لسوابق تسريب. يرجى مراجعة الإدارة."
    if is_blacklisted(db, name):  return f"⚠️ الاسم '{name}' محظور لسوابق تسريب. يرجى مراجعة الإدارة."
    if is_blacklisted(db, text):  return f"⚠️ النص '{text}' محظور لاحتوائه على بيانات مسربة."
    return None


def update_user_coins(
    db:          Session,
    user_id:     int,
    amount:      float,
    tx_type:     models.TransactionType,
    description: Optional[str] = None,
    material_id: Optional[int] = None,
) -> Optional[models.User]:
    """
    تحديث رصيد المستخدم وتسجيل الحركة في الـ Ledger.
    الـ amount ممكن يكون موجب (إضافة) أو سالب (سحب).
    """
    user = get_user_by_id(db, user_id)
    if not user:
        return None

    # تحديث الرصيد
    new_balance = float(user.coins) + float(amount)
    if new_balance < 0:
        raise ValueError("الرصيد غير كافٍ. لا يمكن أن يكون الرصيد بالسالب.")
    user.coins = new_balance

    # تسجيل الحركة
    tx = models.CoinTransaction(
        user_id     = user_id,
        amount      = amount,
        type        = tx_type,
        description = description,
        material_id = material_id,
    )
    db.add(tx)
    
    db.commit()
    db.refresh(user)
    return user


def get_user_coin_history(
    db:      Session,
    user_id: int,
    limit:   int = 50,
) -> list[models.CoinTransaction]:
    """جلب سجل حركات الكوينز لمستخدم"""
    return (
        db.query(models.CoinTransaction)
        .options(joinedload(models.CoinTransaction.material))
        .filter(models.CoinTransaction.user_id == user_id)
        .order_by(models.CoinTransaction.created_at.desc())
        .limit(limit)
        .all()
    )


# ================================================================
# CRUD — MATERIALS
# ================================================================

def get_material(db: Session, material_id: int) -> Optional[models.Material]:
    """جلب ملف بالـ ID مع بيانات الرافع (eager loading)"""
    return (
        db.query(models.Material)
        .options(joinedload(models.Material.uploader))
        .filter(models.Material.id == material_id)
        .first()
    )


def get_published_materials(
    db:       Session,
    skip:     int = 0,
    limit:    int = 20,
) -> tuple[list[models.Material], int]:
    """
    جلب الملفات المنشورة للمتجر مع pagination.
    بيرجع (قائمة الملفات، إجمالي العدد).
    """
    query = (
        db.query(models.Material)
        .options(joinedload(models.Material.uploader))
        .filter(models.Material.is_published == True)
        .order_by(models.Material.created_at.desc())
    )
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return items, total


def get_all_materials(
    db:    Session,
    skip:  int = 0,
    limit: int = 50,
) -> tuple[list[models.Material], int]:
    """جلب كل الملفات (للـ Admin) بما فيها غير المنشورة"""
    query = (
        db.query(models.Material)
        .options(joinedload(models.Material.uploader))
        .order_by(models.Material.created_at.desc())
    )
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return items, total


def create_material(
    db:          Session,
    data:        schemas.MaterialCreate,
    uploader_id: int,
    pdf_path:    str,
    total_pages: int,
    cover_image_path: Optional[str] = None,
) -> models.Material:
    """
    إنشاء سجل ملف جديد في قاعدة البيانات.
    الـ pdf_path هو المسار على الـ server بعد رفع الملف.
    """
    material = models.Material(
        uploaded_by       = uploader_id,
        title             = data.title,
        tag               = data.tag,
        description       = data.description,
        price             = data.price,
        price_coins       = data.price_coins,
        original_pdf_path = pdf_path,
        total_pages       = total_pages,
        is_published      = False,  # مش منشور تلقائياً
        compression_enabled = data.compression_enabled,
        cover_image_path  = cover_image_path,
        page_frame_path   = data.page_frame_path,
    )
    db.add(material)
    db.commit()
    db.refresh(material)
    return material


def update_material(
    db:          Session,
    material_id: int,
    data:        schemas.MaterialUpdate,
) -> Optional[models.Material]:
    """تعديل بيانات ملف — بس الحقول اللي اتبعتت"""
    material = get_material(db, material_id)
    if not material:
        return None

    # استخدام exclude_unset لتمكين مسح حقول مثل التاج (بإرسال null)
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(material, field, value)

    db.commit()
    db.refresh(material)
    return material


def delete_material(db: Session, material_id: int) -> bool:
    """
    حذف ملف من قاعدة البيانات والـ cascade هيحذف الـ layouts والـ tokens.
    بيرجع True لو اتحذف، False لو مش موجود.
    """
    material = get_material(db, material_id)
    if not material:
        return False
    db.delete(material)
    db.commit()
    return True


# ================================================================
# CRUD — STAMP LAYOUTS
# ================================================================

def get_layout(db: Session, layout_id: int) -> Optional[models.StampLayout]:
    """جلب تنسيق ختم بالـ ID"""
    return db.query(models.StampLayout).filter(models.StampLayout.id == layout_id).first()


def get_default_layout(db: Session, material_id: int, layout_type: models.LayoutType = models.LayoutType.DEFAULT) -> Optional[models.StampLayout]:
    """جلب التنسيق الافتراضي لمادة معينة حسب النوع"""
    ly = (
        db.query(models.StampLayout)
        .filter(
            models.StampLayout.material_id == material_id,
            models.StampLayout.layout_type == layout_type,
        )
        .first()
    )
    if ly:
        return ly
        
    # fallback to DEFAULT if the requested type is not found
    if layout_type != models.LayoutType.DEFAULT:
        return (
            db.query(models.StampLayout)
            .filter(
                models.StampLayout.material_id == material_id,
                models.StampLayout.layout_type == models.LayoutType.DEFAULT,
            )
            .first()
        )
    return None


def create_layout(
    db:         Session,
    data:       schemas.StampLayoutCreate,
    creator_id: int,
) -> models.StampLayout:
    """
    إنشاء تنسيق أختام جديد لمادة معينة.
    لو فيه تنسيق من نفس النوع موجود للمادة، بنحدثه بدل ما نكرره.
    """
    existing = (
        db.query(models.StampLayout)
        .filter(models.StampLayout.material_id == data.material_id)
        .filter(models.StampLayout.layout_type == data.layout_type)
        .first()
    )

    if existing:
        existing.stamp_elements = [el.model_dump() for el in data.stamp_elements]
        existing.created_by = creator_id
        db.commit()
        db.refresh(existing)
        return existing

    layout = models.StampLayout(
        material_id    = data.material_id,
        created_by     = creator_id,
        layout_type    = data.layout_type,
        stamp_elements = [el.model_dump() for el in data.stamp_elements],
    )
    db.add(layout)
    db.commit()
    db.refresh(layout)
    return layout


def update_layout(
    db:        Session,
    layout_id: int,
    data:      schemas.StampLayoutUpdate,
) -> Optional[models.StampLayout]:
    """تحديث عناصر التنسيق — بنستبدل القائمة كلها"""
    layout = get_layout(db, layout_id)
    if not layout:
        return None
    layout.stamp_elements = [el.model_dump() for el in data.stamp_elements]
    db.commit()
    db.refresh(layout)
    return layout


def clone_layout_as_custom(
    db:         Session,
    layout_id:  int,
    buyer_id:   int,
    new_elements: list[schemas.StampElement],
) -> models.StampLayout:
    """
    نسخ تنسيق الـ Admin وحفظه كـ custom للمشتري.
    بيُستخدم لما العميل يعدّل مواضع الأختام قبل الشراء.
    """
    original = get_layout(db, layout_id)
    custom = models.StampLayout(
        material_id    = original.material_id,
        created_by     = buyer_id,
        layout_type    = models.LayoutType.CUSTOM,
        stamp_elements = [el.model_dump() for el in new_elements],
    )
    db.add(custom)
    db.commit()
    db.refresh(custom)
    return custom


# ================================================================
# CRUD — PURCHASES
# ================================================================

def get_purchase(db: Session, purchase_id: int) -> Optional[models.Purchase]:
    """جلب عملية شراء بالـ ID مع البيانات المرتبطة"""
    return (
        db.query(models.Purchase)
        .options(
            joinedload(models.Purchase.material),
            joinedload(models.Purchase.buyer),
        )
        .filter(models.Purchase.id == purchase_id)
        .first()
    )


def get_user_purchases(
    db:      Session,
    user_id: int,
    skip:    int = 0,
    limit:   int = 20,
) -> tuple[list[models.Purchase], int]:
    """جلب كل مشتريات مستخدم معين"""
    query = (
        db.query(models.Purchase)
        .options(joinedload(models.Purchase.material))
        .filter(models.Purchase.buyer_id == user_id)
        .filter(models.Purchase.is_hidden == False)
        .order_by(models.Purchase.purchased_at.desc())
    )
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return items, total


def create_purchase(
    db:      Session,
    data:    schemas.PurchaseCreate,
    buyer_id: int,
    amount:  float,
) -> models.Purchase:
    """
    إنشاء عملية شراء جديدة.
    الحالة الأولية: PENDING — تتغير لـ PROCESSING بعد تأكيد الدفع.
    """
    # تنظيف رقم العملية لتجنب تعارض الـ UNIQUE constraint مع النصوص الفارغة في SQLite
    tx_id = (data.transaction_id.strip() or None) if (data.transaction_id and isinstance(data.transaction_id, str)) else None

    purchase = models.Purchase(
        buyer_id          = buyer_id,
        material_id       = data.material_id,
        stamp_layout_id   = data.stamp_layout_id,
        buyer_name_stamp  = data.buyer_name_stamp,
        buyer_phone_stamp = data.buyer_phone_stamp,
        buyer_phone_stamp_2 = data.buyer_phone_stamp_2,
        watermark_text    = data.watermark_text,
        doc_name_stamp    = data.doc_name_stamp,
        watermark_type    = data.watermark_type,
        transaction_id    = tx_id,
        payment_method    = data.payment_method,
        amount_paid       = amount,
        status            = models.PurchaseStatus.COMPLETED, # أون-ذا-فلاي: تكتمل العملية فوراً بدون ختم
    )
    db.add(purchase)

    # لو الدفع بالكوينز، نسحبهم فوراً
    if data.payment_method == models.PaymentMethod.COINS:
        update_user_coins(
            db          = db,
            user_id     = buyer_id,
            amount      = -float(amount),
            tx_type     = models.TransactionType.PURCHASE,
            description = f"شراء مادة: {purchase.material_id}",
            material_id = purchase.material_id,
        )

    db.commit()
    db.refresh(purchase)
    return purchase


def update_purchase_status(
    db:          Session,
    purchase_id: int,
    status:      models.PurchaseStatus,
    output_path: Optional[str] = None,
) -> Optional[models.Purchase]:
    """
    تحديث حالة عملية الشراء.
    بيُستدعى من الـ stamping engine بعد الانتهاء من الختم.
    """
    purchase = get_purchase(db, purchase_id)
    if not purchase:
        return None

    purchase.status = status

    # لو اكتمل الختم، نسجل المسار ووقت الاكتمال
    if status == models.PurchaseStatus.COMPLETED:
        purchase.output_pdf_path = output_path
        purchase.completed_at    = datetime.utcnow()

    db.commit()
    db.refresh(purchase)
    return purchase


def hide_purchase(db: Session, purchase_id: int) -> bool:
    """إخفاء عملية الشراء (حذف صوري)"""
    purchase = get_purchase(db, purchase_id)
    if not purchase:
        return False
    purchase.is_hidden = True
    db.commit()
    return True


def record_hidden_mark(
    db:          Session,
    purchase_id: int,
    page_number: int,
    x_pct:       float,
    y_pct:       float,
    mark_code:   Optional[str] = None,
    mark_type:   models.MarkType = models.MarkType.INVISIBLE_TEXT,
) -> models.HiddenMark:
    """
    تسجيل علامة مخفية بعد إضافتها للملف.
    """
    code = mark_code if mark_code else str(uuid.uuid4())
    mark = models.HiddenMark(
        purchase_id = purchase_id,
        mark_code   = code,
        page_number = page_number,
        x_position  = x_pct,
        y_position  = y_pct,
        mark_type   = mark_type,
    )
    db.add(mark)
    db.commit()
    db.refresh(mark)
    return mark


def find_purchase_by_mark_code(db: Session, mark_code: str) -> Optional[models.Purchase]:
    """
    تتبع التسريب — البحث عن عملية الشراء بواسطة كود العلامة المخفية.
    لو لقينا الكود في ملف مسرّب، نعرف مين اشتراه.
    """
    mark = (
        db.query(models.HiddenMark)
        .filter(models.HiddenMark.mark_code == mark_code)
        .first()
    )
    if not mark:
        return None
    return get_purchase(db, mark.purchase_id)


# ================================================================
# CRUD — USER MANAGEMENT (Admin Only Actions)
# ================================================================

def set_user_active_status(db: Session, user_id: int, is_active: bool) -> Optional[models.User]:
    """تفعيل أو تجميد حساب مستخدم"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user: return None
    user.is_active = is_active
    db.commit()
    db.refresh(user)
    return user

def set_user_role(db: Session, user_id: int, role: models.UserRole) -> Optional[models.User]:
    """تغيير دور المستخدم (مثلاً ترقية لـ Admin)"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user: return None
    user.role = role
    db.commit()
    db.refresh(user)
    return user


# ================================================================
# CRUD — PREVIEW TOKENS
# ================================================================

def create_preview_token(
    db:          Session,
    material_id: int,
    user_id:     int,
    valid_mins:  int = 30,
) -> models.PreviewToken:
    """
    إنشاء توكن معاينة مؤقت وتطبيق خوارزمية المعاينة الذكية (Smart Preview).
    الـ token عشوائي بالكامل — مش JWT عشان نتحكم في إلغائه.
    """
    # 1. استخراج عدد صفحات المذكرة الكلي (N)
    material = get_material(db, material_id)
    n_pages = material.total_pages if material and material.total_pages else 10

    # 2. حساب عدد صفحات العينة بشكل متناسب:
    #    - 15% من الصفحات الكلية
    #    - حد أدنى: 10 صفحات (أو كل الصفحات لو الملف صغير)
    #    - حد أقصى: 50 صفحة
    raw_count = max(10, int(n_pages * 0.15))
    c_pages   = min(raw_count, 50, n_pages)

    # 3. توليد قائمة الصفحات العشوائية
    import random as _rnd

    # الصفحة الأولى دايماً مسموح بيها (الغلاف)
    allowed_set = {1}

    if n_pages > 1:
        # باقي الصفحات تُختار عشوائياً من كل الملف (من صفحة 2 للأخيرة)
        remaining_pool = list(range(2, n_pages + 1))
        extra_count    = min(c_pages - 1, len(remaining_pool))
        extra_pages    = _rnd.sample(remaining_pool, extra_count)
        allowed_set.update(extra_pages)

    allowed = sorted(allowed_set)

    token = models.PreviewToken(
        material_id   = material_id,
        user_id       = user_id,
        token         = secrets.token_urlsafe(32),  # 32 بايت عشوائي
        allowed_pages = allowed,
        expires_at    = datetime.utcnow() + timedelta(minutes=valid_mins),
    )
    db.add(token)
    db.commit()
    db.refresh(token)
    return token


def get_valid_preview_token(db: Session, token: str) -> Optional[models.PreviewToken]:
    """
    جلب توكن المعاينة لو كان صالح وغير منتهي.
    بيُستدعى قبل كل عملية معاينة.
    """
    preview = (
        db.query(models.PreviewToken)
        .options(joinedload(models.PreviewToken.material))
        .filter(
            models.PreviewToken.token      == token,
            models.PreviewToken.expires_at >  datetime.utcnow(),  # غير منتهي
        )
        .first()
    )
    return preview


def revoke_preview_token(db: Session, token: str) -> bool:
    """
    إلغاء توكن المعاينة — بنعمله منتهي على طول.
    بيُستدعى بعد انتهاء الجلسة أو تسجيل الخروج.
    """
    preview = db.query(models.PreviewToken).filter(
        models.PreviewToken.token == token
    ).first()
    if not preview:
        return False

    # بنجعل الـ expires_at في الماضي بدل الحذف الكامل
    # عشان نحتفظ بسجل المعاينات للـ analytics
    preview.expires_at = datetime.utcnow() - timedelta(seconds=1)
    db.commit()
    return True


# ================================================================
# CRUD — LAYOUT PRESETS
# ================================================================

def get_presets(db: Session) -> list[models.LayoutPreset]:
    """جلب كل القوالب الجاهزة"""
    return db.query(models.LayoutPreset).order_by(models.LayoutPreset.created_at.desc()).all()


def create_preset(
    db:         Session,
    data:       schemas.LayoutPresetCreate,
    creator_id: int,
) -> models.LayoutPreset:
    """إنشاء قالب أختام جديد"""
    preset = models.LayoutPreset(
        name           = data.name,
        created_by     = creator_id,
        stamp_elements = [el.model_dump() for el in data.stamp_elements],
    )
    db.add(preset)
    db.commit()
    db.refresh(preset)
    return preset


def delete_preset(db: Session, preset_id: int) -> bool:
    """حذف قالب جاهز"""
    preset = db.query(models.LayoutPreset).filter(models.LayoutPreset.id == preset_id).first()
    if not preset:
        return False
    db.delete(preset)
    db.commit()
    return True
# ================================================================
# CRUD — BACKGROUND JOBS
# ================================================================

def create_background_job(
    db:      Session,
    user_id: int,
    job_id:  str,
    label:   str,
) -> models.BackgroundJob:
    """إنشاء سجل وظيفة خلفية جديد"""
    job = models.BackgroundJob(
        user_id = user_id,
        job_id  = job_id,
        label   = label,
        status  = "processing",
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def update_background_job(
    db:          Session,
    job_id:      str,
    status:      str,
    output_path: Optional[str] = None,
    error:       Optional[str] = None,
) -> Optional[models.BackgroundJob]:
    """تحديث حالة الوظيفة ونتائجها"""
    job = db.query(models.BackgroundJob).filter(models.BackgroundJob.job_id == job_id).first()
    if not job:
        return None
    
    job.status        = status
    job.output_path   = output_path
    job.error_message = error
    db.commit()
    db.refresh(job)
    return job


def get_user_background_jobs(
    db:      Session,
    user_id: int,
    limit:   int = 10,
) -> list[models.BackgroundJob]:
    """جلب آخر الوظائف لمستخدم معين"""
    return (
        db.query(models.BackgroundJob)
        .filter(models.BackgroundJob.user_id == user_id)
        .order_by(models.BackgroundJob.created_at.desc())
        .limit(limit)
        .all()
    )


def get_background_job_by_id(db: Session, job_id: str) -> Optional[models.BackgroundJob]:
    """جلب تفاصيل وظيفة معينة بالـ UUID"""
    return db.query(models.BackgroundJob).filter(models.BackgroundJob.job_id == job_id).first()

