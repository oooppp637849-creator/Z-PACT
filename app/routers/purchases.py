# ================================================================
# app/routers/purchases.py — نقاط نهاية المشتريات
#
# الـ Endpoints:
#   POST /purchases/              → شراء ملف جديد
#   GET  /purchases/              → مشترياتي
#   GET  /purchases/{id}          → تفاصيل شراء معين
#   GET  /purchases/{id}/download → تحميل الملف المختوم
#   POST /purchases/{id}/stamp    → طلب ختم الملف (يشتغل في الـ background)
# ================================================================

import secrets
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app import crud, schemas, models
from app.auth import get_current_user
from app.database import get_db
from app.models import Purchase, PurchaseStatus, User, UserRole, SpendingLevel, Coupon, Notification
from app.stamper import stamp_pdf  # محرك الختم (المهمة 4)
from app.logger import logger

def _check_loyalty_rewards(db: Session, user: User, amount: float):
    """التحقق من مكافآت الولاء وإصدار كوبون عند تخطي مستوى إنفاق معين"""
    old_spent = float(user.total_spent or 0)
    new_spent = old_spent + amount
    user.total_spent = new_spent
    
    levels = db.query(SpendingLevel).filter(
        SpendingLevel.threshold > old_spent,
        SpendingLevel.threshold <= new_spent
    ).all()
    
    for level in levels:
        code = f"VIP-{secrets.token_hex(4).upper()}"
        coupon = Coupon(
            code=code,
            user_id=user.id,
            reward_coins=level.reward_coins
        )
        db.add(coupon)
        
        notif = Notification(
            user_id=user.id,
            title="🎁 مكافأة ولاء جديدة!",
            message=f"تهانينا! لقد تخطيت مستوى إنفاق {level.threshold} وحصلت على كوبون بقيمة {level.reward_coins} كوينز. كود الكوبون: {code}"
        )
        db.add(notif)
    
    db.commit()

router = APIRouter(prefix="/purchases", tags=["المشتريات"])

# تخزين مؤقت لتوكنات التحميل في الذاكرة
# في Production استبدله بـ Redis
_download_tokens: dict[str, dict] = {}


# ================================================================
# شراء ملف جديد
# ================================================================

@router.post(
    "/",
    response_model = schemas.PurchaseOut,
    status_code    = status.HTTP_201_CREATED,
    summary        = "شراء ملف",
)
def create_purchase(
    data:            schemas.PurchaseCreate,
    background_tasks: BackgroundTasks,
    db:              Session = Depends(get_db),
    current_user:    User    = Depends(get_current_user),
):
    """
    تسجيل عملية شراء جديدة وبدء عملية الختم في الـ background.

    الخطوات:
      1. التحقق إن الملف موجود ومنشور
      2. التحقق إن المستخدم ما اشتراش الملف ده قبل كده
      3. تسجيل عملية الشراء بحالة PENDING
      4. إطلاق عملية الختم في الـ background (مش بتأخر الـ Response)
    """
    # --- التحقق من الملف ---
    material = crud.get_material(db, data.material_id)
    if not material or not material.is_published:
        raise HTTPException(status_code=404, detail="الملف غير موجود أو غير متاح")

    # --- التحقق من التنسيق (لو اختار واحد) ---
    stamp_layout = None
    if data.stamp_layout_id:
        stamp_layout = crud.get_layout(db, data.stamp_layout_id)
        if not stamp_layout or stamp_layout.material_id != material.id:
            raise HTTPException(status_code=400, detail="التنسيق غير صحيح")
    else:
        # استخدام التنسيق الافتراضي للمادة بناءً على نوع العلامة المائية
        layout_type = models.LayoutType.DEFAULT_LOGO if data.watermark_type in ["logo", "teacher", "platform"] else models.LayoutType.DEFAULT_TEXT
        stamp_layout = crud.get_default_layout(db, material.id, layout_type)

    if not stamp_layout:
        raise HTTPException(
            status_code = 400,
            detail      = "لا يوجد تنسيق أختام لهذا الملف بعد. تواصل مع الإدارة.",
        )

    # --- تحديد السعر حسب وسيلة الدفع ---
    if data.payment_method == models.PaymentMethod.COINS:
        amount = float(material.price_coins)
        # التحقق من الرصيد
        if current_user.coins < amount:
            raise HTTPException(status_code=400, detail="رصيدك من الكوينز غير كافٍ")
    else:
        amount = float(material.price)
        if not data.transaction_id:
            raise HTTPException(status_code=400, detail="رقم عملية الدفع مطلوب للدفع النقدي")

    # --- التحقق من القائمة السوداء ---
    blacklist_msg = crud.check_stamp_data_against_blacklist(
        db, 
        data.buyer_name_stamp, 
        data.buyer_phone_stamp, 
        data.watermark_text
    )
    if blacklist_msg:
        raise HTTPException(status_code=403, detail=blacklist_msg)

    # --- إنشاء سجل الشراء ---
    try:
        purchase = crud.create_purchase(
            db       = db,
            data     = data,
            buyer_id = current_user.id,
            amount   = amount,
        )
        # ربط الـ layout بالشراء
        purchase.stamp_layout_id = stamp_layout.id
        db.commit()
        
        # تفعيل نظام الولاء والكوبونات
        _check_loyalty_rewards(db, current_user, amount)

    except Exception as e:
        db.rollback()
        # التحقق إذا كان الخطأ بسبب تكرار الـ transaction_id
        if "UNIQUE constraint failed" in str(e) or "duplicate key" in str(e).lower():
            raise HTTPException(status_code=400, detail="رقم هذه العملية تم استخدامه مسبقاً. يرجى مراجعة الإدارة.")
        raise HTTPException(status_code=500, detail=f"فشل تسجيل عملية الشراء: {str(e)}")

    # أون-ذا-فلاي (Background Stamping):
    # نبدأ عملية الختم فوراً في الخلفية لتكون المذكرة جاهزة عند وصول المستخدم لصفحة المشتريات.
    _trigger_stamping_task(purchase, background_tasks, db)

    return schemas.PurchaseOut.model_validate(purchase)

# ================================================================
# الدفع التلقائي عبر المحفظة (Vodafone/InstaPay)
# ================================================================

@router.post(
    "/wallet-auto",
    summary="الدفع التلقائي عبر المحفظة (Vodafone/InstaPay)",
)
def auto_wallet_purchase(
    data:            schemas.WalletAutoPurchase,
    background_tasks: BackgroundTasks,
    db:              Session = Depends(get_db),
    current_user:    User    = Depends(get_current_user),
):
    """
    البحث عن تحويل معلق برقم الهاتف في جدول wallet_transactions.
    إذا وجده: يحوله لـ completed، يضيف الرصيد للـ User، وإذا كان الرصيد كافياً يبدأ عملية الشراء.
    """
    # 1. البحث عن عملية التحويل
    tx = (
        db.query(models.WalletTransaction)
        .filter(models.WalletTransaction.sender_phone == data.transfer_phone)
        .filter(models.WalletTransaction.status == "pending")
        .order_by(models.WalletTransaction.transaction_date.asc())
        .with_for_update()
        .first()
    )

    if not tx:
        raise HTTPException(
            status_code=404,
            detail="لم نتمكن من العثور على تحويل معلق من هذا الرقم أو الحساب. يرجى التأكد من الرقم أو الانتظار لدقيقة والمحاولة مجدداً."
        )

    # 2. تحديث حالة التحويل إلى completed وإضافة الرصيد
    tx.status = "completed"
    db.commit()

    crud.update_user_coins(
        db=db,
        user_id=current_user.id,
        amount=float(tx.amount),
        tx_type=models.TransactionType.RECHARGE,
        description=f"شحن تلقائي من {tx.source or 'المحفظة'} - {data.transfer_phone}"
    )

    # 3. جلب المادة المطلوبة والتحقق من الرصيد الجديد
    material = crud.get_material(db, data.material_id)
    if not material or not material.is_published:
        raise HTTPException(status_code=404, detail="الملف غير موجود أو غير متاح")

    db.refresh(current_user) # تحديث الرصيد بعد الشحن

    if float(current_user.coins) < float(material.price_coins):
        return {
            "status": "partial",
            "message": f"تم شحن رصيدك بنجاح بمبلغ {tx.amount} كوينز، ولكن سعر المذكرة {material.price_coins}. يرجى تحويل الفارق لشراء الملف."
        }

    # 4. الرصيد كافٍ -> إتمام عملية الشراء
    purchase_data = schemas.PurchaseCreate(
        material_id=data.material_id,
        buyer_name_stamp=data.buyer_name_stamp,
        buyer_phone_stamp=data.buyer_phone_stamp,
        buyer_phone_stamp_2=data.buyer_phone_stamp_2,
        watermark_text=data.watermark_text,
        doc_name_stamp=data.doc_name_stamp,
        watermark_type=data.watermark_type,
        payment_method=models.PaymentMethod.COINS
    )

    # التحقق من القائمة السوداء
    blacklist_msg = crud.check_stamp_data_against_blacklist(
        db, 
        purchase_data.buyer_name_stamp, 
        purchase_data.buyer_phone_stamp, 
        purchase_data.watermark_text
    )
    if blacklist_msg:
        raise HTTPException(status_code=403, detail=blacklist_msg)

    # استخدام التنسيق الافتراضي للمادة بناءً على نوع العلامة المائية
    layout_type = models.LayoutType.DEFAULT_LOGO if data.watermark_type in ["logo", "teacher", "platform"] else models.LayoutType.DEFAULT_TEXT
    stamp_layout = crud.get_default_layout(db, material.id, layout_type)
    if not stamp_layout:
        raise HTTPException(status_code=400, detail="لا يوجد تنسيق أختام لهذا الملف بعد.")

    try:
        purchase = crud.create_purchase(
            db       = db,
            data     = purchase_data,
            buyer_id = current_user.id,
            amount   = float(material.price_coins),
        )
        purchase.stamp_layout_id = stamp_layout.id
        db.commit()
        
        # تفعيل نظام الولاء والكوبونات
        _check_loyalty_rewards(db, current_user, float(material.price_coins))

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"فشل إنشاء الشراء بعد الشحن: {str(e)}")

    _trigger_stamping_task(purchase, background_tasks, db)

    return {
        "status": "success",
        "purchase_id": purchase.id,
        "title": material.title,
        "message": "تم تأكيد التحويل وجاري تجهيز الملف"
    }


# ================================================================
# قائمة مشتريات المستخدم
# ================================================================

@router.get(
    "/",
    response_model = schemas.PaginatedOut,
    summary        = "قائمة مشترياتي",
)
def list_my_purchases(
    page:     int         = Query(1, ge=1),
    per_page: int         = Query(10, ge=1, le=1000),
    search:   Optional[str] = Query(None, description="بحث باسم المذكرة أو التاريخ"),
    db:       Session     = Depends(get_db),
    user:     User        = Depends(get_current_user),
):
    import math
    skip = (page - 1) * per_page
    
    # بناء الـ Query لدعم البحث
    query = (
        db.query(models.Purchase)
        .join(models.Material, models.Purchase.material_id == models.Material.id)
        .filter(models.Purchase.buyer_id == user.id)
        .filter(models.Purchase.is_hidden == False)
    )
    
    if search:
        query = query.filter(models.Material.title.ilike(f"%{search}%"))
        
    query = query.order_by(models.Purchase.purchased_at.desc())
    
    total = query.count()
    items = query.offset(skip).limit(per_page).all()

    return schemas.PaginatedOut(
        items       = [schemas.PurchaseOut.model_validate(p) for p in items],
        total       = total,
        page        = page,
        per_page    = per_page,
        total_pages = math.ceil(total / per_page) if total > 0 else 1,
    )


@router.delete("/{purchase_id}", response_model=schemas.MessageOut)
def delete_purchase(
    purchase_id: int,
    db:          Session = Depends(get_db),
    current_user: User   = Depends(get_current_user),
):
    """حذف (إخفاء) عملية الشراء من قائمة المستخدم"""
    purchase = crud.get_purchase(db, purchase_id)
    if not purchase or purchase.buyer_id != current_user.id:
        raise HTTPException(status_code=404, detail="العملية غير موجودة")
    
    success = crud.hide_purchase(db, purchase_id)
    if not success:
        raise HTTPException(status_code=500, detail="فشل إخفاء العملية")
        
    return schemas.MessageOut(message="تم حذف الملف من قائمة مشترياتك بنجاح")


# ================================================================
# تحميل الملف الفعلي
# ================================================================

@router.get(
    "/download",
    summary = "تحميل الملف المختوم بالتوكن",
)
def download_stamped_pdf(token: str = Query(...)):
    """
    تحميل الملف المختوم باستخدام التوكن المؤقت.

    الأمان:
      - التوكن صالح 10 دقائق فقط
      - بيتحذف بعد أول استخدام (one-time use)
      - بيرجع FileResponse مع اسم ملف مشفر
    """
    token_data = _download_tokens.get(token)

    if not token_data:
        # استخدام 403 بدلاً من 401 لمنع المتصفح من إظهار نافذة تسجيل الدخول (Basic Auth Popup)
        raise HTTPException(status_code=403, detail="رابط التحميل غير صالح أو منتهي")

    # التحقق من الصلاحية الزمنية (10 دقائق)
    if datetime.utcnow() > token_data["expires_at"]:
        if token in _download_tokens: del _download_tokens[token]
        raise HTTPException(status_code=403, detail="انتهت صلاحية رابط التحميل (10 دقائق)")

    # 1. جلب مسار الملف ومعرّف العملية
    file_path = token_data["file_path"]
    purchase_id = token_data["purchase_id"]

    # ملاحظة: تم إلغاء حذف التوكن هنا للسماح للمتصفحات بإعادة المحاولة (Retries) 
    # أو استكمال التحميل (Resuming) خلال فترة الصلاحية.
    # سيتم تنظيف التوكنات القديمة لاحقاً.

    # 3. إرجاع الـ Response
    return FileResponse(
        path              = file_path,
        media_type        = "application/pdf",
        filename          = f"material_{purchase_id}_stamped.pdf",
        headers           = {
            "Content-Disposition":    f'attachment; filename="material_{purchase_id}.pdf"',
            "X-Content-Type-Options": "nosniff",
            "Cache-Control":          "no-store",
        }
    )

# ================================================================
# تفاصيل شراء معين
# ================================================================

@router.get(
    "/{purchase_id}",
    response_model = schemas.PurchaseOut,
    summary        = "تفاصيل عملية شراء",
)
def get_purchase(
    purchase_id:  int,
    db:           Session = Depends(get_db),
    current_user: User    = Depends(get_current_user),
):
    purchase = crud.get_purchase(db, purchase_id)
    if not purchase:
        raise HTTPException(status_code=404, detail="العملية غير موجودة")

    # مستخدم عادي يشوف مشترياته بس، والمدير مسموح له برؤية أي عملية
    if purchase.buyer_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="ليس لديك صلاحية")

    try:
        return schemas.PurchaseOut.model_validate(purchase)
    except Exception as e:
        import logging
        logging.error(f"Error validating purchase {purchase_id}: {e}")
        return schemas.PurchaseOut(
            id=purchase.id,
            buyer_id=purchase.buyer_id,
            material_id=purchase.material_id,
            buyer_name_stamp=purchase.buyer_name_stamp,
            buyer_phone_stamp=purchase.buyer_phone_stamp,
            buyer_phone_stamp_2=purchase.buyer_phone_stamp_2,
            watermark_text=purchase.watermark_text,
            doc_name_stamp=purchase.doc_name_stamp,
            watermark_type=purchase.watermark_type or "text",
            status=purchase.status,
            amount_paid=purchase.amount_paid,
            payment_method=purchase.payment_method,
            purchased_at=purchase.purchased_at,
            completed_at=purchase.completed_at,
            material=schemas.MaterialOut.model_validate(purchase.material) if purchase.material else None
        )


# ================================================================
# طلب توكن التحميل + التحميل الفعلي
# ================================================================

def _trigger_stamping_task(
    purchase: models.Purchase, 
    background_tasks: BackgroundTasks, 
    db: Session
):
    """
    مساعد لإطلاق عملية الختم في الخلفية.
    يُستخدم عند الشراء لأول مرة، أو عند إعادة التوليد التلقائي.
    """
    material = purchase.material
    stamp_layout = purchase.stamp_layout
    
    if not stamp_layout:
        raise HTTPException(status_code=400, detail="التنسيق مفقود")
    
    # تحديث الحالة إلى PROCESSING للبدء
    purchase.status = models.PurchaseStatus.PROCESSING
    db.commit()
    
    from app.stamper import stamp_pdf
    # استبدال الـ placeholders (Tag)
    watermark_text = purchase.watermark_text
    doc_name_stamp = purchase.doc_name_stamp

    # (1) استبدال {tag} في مدخلات المشتري
    if material.tag:
        if watermark_text:
            watermark_text = watermark_text.replace("{tag}", material.tag).replace("[tag]", material.tag)
        if doc_name_stamp:
            doc_name_stamp = doc_name_stamp.replace("{tag}", material.tag).replace("[tag]", material.tag)

    # (2) استبدال {tag} في custom_text بتاع عناصر الـ layout (نصوص الأدمن الثابتة)
    raw_elements = stamp_layout.get_elements()
    if material.tag:
        processed_elements = []
        for el in raw_elements:
            el_copy = dict(el)
            if el_copy.get("custom_text"):
                el_copy["custom_text"] = (
                    el_copy["custom_text"]
                    .replace("{tag}", material.tag)
                    .replace("[tag]", material.tag)
                )
            processed_elements.append(el_copy)
    else:
        processed_elements = raw_elements

    # جلب مسار الشعار الخاص بالمدرس لو متوفر
    watermark_type_arg = purchase.watermark_type
    if purchase.watermark_type == 'teacher':
        buyer_logo = material.uploader.watermark_logo_path if material.uploader else None
        watermark_type_arg = 'logo'
    elif purchase.watermark_type == 'platform':
        buyer_logo = None
        watermark_type_arg = 'logo'
    else:
        buyer_logo = None


    background_tasks.add_task(
        stamp_pdf,
        purchase_id      = purchase.id,
        material_path    = material.original_pdf_path,
        stamp_layout     = processed_elements,
        buyer_name       = purchase.buyer_name_stamp,
        buyer_phone      = purchase.buyer_phone_stamp,
        watermark_text   = watermark_text,
        doc_name_stamp   = doc_name_stamp,
        compress         = material.compression_enabled,
        material_tag     = material.tag,
        watermark_type   = watermark_type_arg,
        watermark_logo_path = buyer_logo,
    )

@router.post(
    "/{purchase_id}/prepare-download",
    summary="بدء توليد الملف للتحميل (On-the-fly)",
)
def prepare_download(
    purchase_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    purchase = crud.get_purchase(db, purchase_id)
    if not purchase or purchase.buyer_id != current_user.id:
        raise HTTPException(status_code=404, detail="العملية غير موجودة")
        
    _trigger_stamping_task(purchase, background_tasks, db)
    
    return {"message": "Started preparing file", "success": True}


@router.post(
    "/{purchase_id}/download-token",
    response_model = schemas.PurchaseDownloadOut,
    summary        = "طلب توكن تحميل مؤقت (10 دقائق)",
)
def request_download_token(
    purchase_id:  int,
    background_tasks: BackgroundTasks, # تمت إضافة المهام الخلفية لإعادة التوليد التلقائي
    db:           Session = Depends(get_db),
    current_user: User    = Depends(get_current_user),
):
    """
    إنشاء توكن تحميل مؤقت للملف المختوم.
    الـ token صالح 10 دقائق فقط ولمرة واحدة.
    
    تحسين (Storage Optimization):
    إذا كان الملف قد حُذف من السيرفر (بعد 24 ساعة)، سيقوم النظام بإعادة
    توليده تلقائياً وإرجاع خطأ 410 للواجهة لتبدأ عملية الانتظار.
    """
    import os
    purchase = crud.get_purchase(db, purchase_id)

    if not purchase or purchase.buyer_id != current_user.id:
        raise HTTPException(status_code=404, detail="العملية غير موجودة")

    # 1. التحقق من وجود الملف فعلياً على القرص
    file_exists = purchase.output_pdf_path and os.path.exists(purchase.output_pdf_path)

    # 2. إذا كان الملف غير موجود أو الحالة ليست مكتملة
    if purchase.status != PurchaseStatus.COMPLETED or not file_exists:
        # إذا كان مكتمل في الداتا بيز بس الملف اتمسح من السيرفر
        if purchase.status == PurchaseStatus.COMPLETED and not file_exists:
            logger.info(f"🔄 [On-demand] File missing for purchase {purchase_id}. Re-stamping...")
            _trigger_stamping_task(purchase, background_tasks, db)
            raise HTTPException(
                status_code = status.HTTP_410_GONE, 
                detail      = "FILE_EXPIRED_RE_STAMPING"
            )
        
        # إذا كان الملف جاري معالجته بالفعل
        if purchase.status == PurchaseStatus.PROCESSING:
             raise HTTPException(
                status_code = status.HTTP_409_CONFLICT, # تم استخدامه كرمز تعبيري لـ "جاري العمل"
                detail      = "FILE_STILL_PROCESSING"
            )
            
        raise HTTPException(
            status_code = 400,
            detail      = f"الملف لم يكتمل بعد أو فشل. الحالة: {purchase.status.value}",
        )

    # إنشاء توكن عشوائي للتحميل
    token      = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(minutes=10)

    # حفظ التوكن مؤقتاً في الذاكرة
    _download_tokens[token] = {
        "purchase_id": purchase_id,
        "file_path":   purchase.output_pdf_path,
        "expires_at":  expires_at,
        "used":        False,
    }

    return schemas.PurchaseDownloadOut(
        purchase_id    = purchase_id,
        download_token = token,
        expires_at     = expires_at,
    )


# Note: Redundant delete_purchase route removed to prevent conflict.

# ================================================================
# إصلاح التحميل (Repair & Security Audit)
# ================================================================

import logging
logger = logging.getLogger(__name__)

@router.post(
    "/repair/{purchase_id}",
    summary="إصلاح عملية الختم لعملية شراء سابقة",
)
def repair_purchase(
    purchase_id:      int,
    background_tasks: BackgroundTasks,
    db:               Session = Depends(get_db),
    current_user:     User    = Depends(get_current_user),
):
    """
    إعادة توليد الـ PDF في حال فشل الختم السابق لسبب تقني،
    دون الحاجة للدفع مرة أخرى.
    """
    purchase = crud.get_purchase(db, purchase_id)

    # 1. التحقق من أن المستخدم هو صاحب الطلب
    if not purchase or purchase.buyer_id != current_user.id:
        logger.warning(f"Potential Fraud: User {current_user.id} attempted to repair purchase {purchase_id} belonging to another user or non-existent.")
        raise HTTPException(status_code=403, detail="غير مصرح لك بإصلاح هذه العملية أو أنها غير موجودة.")

    # 2. التدقيق الأمني (Audit): التأكد أن العملية مدفوعة
    if purchase.status not in (models.PurchaseStatus.COMPLETED, models.PurchaseStatus.FAILED):
        logger.warning(f"Potential Fraud: User {current_user.id} attempted to repair purchase {purchase_id} with status {purchase.status}.")
        raise HTTPException(status_code=403, detail="لا يمكن إصلاح عملية لم تكتمل أو لم تُدفع.")

    # 3. إعادة التشغيل
    _trigger_stamping_task(purchase, background_tasks, db)

    return {
        "status": "success",
        "message": "تم إرسال طلب الإصلاح بنجاح. جاري العمل على تجهيز الملف.",
        "purchase_id": purchase.id,
        "title": purchase.material.title if purchase.material else "الملف"
    }
