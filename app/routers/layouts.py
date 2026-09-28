# ================================================================
# app/routers/layouts.py — نقاط نهاية تنسيقات الأختام
# ================================================================

from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Query

from app import crud, models, schemas
from app.auth import get_current_user, require_admin
from app.database import get_db

# استخدام prefix لتوحيد المسارات وتجنب التكرار
router = APIRouter(prefix="/layouts", tags=["الأختام والتتبع"])


@router.post("/", response_model=schemas.StampLayoutOut, summary="إنشاء تنسيق أختام (Admin فقط)")
def create_layout(
    data:   schemas.StampLayoutCreate,
    db:     Session = Depends(get_db),
    admin:  models.User = Depends(require_admin),
):
    """إنشاء تنسيق أختام جديد لمادة معينة."""
    layout = crud.create_layout(db, data, creator_id=admin.id)
    return schemas.StampLayoutOut.model_validate(layout)


@router.get("/{layout_id}", response_model=schemas.StampLayoutOut, summary="جلب تنسيق أختام")
def get_layout(
    layout_id: int,
    db:        Session = Depends(get_db),
    _user:     models.User = Depends(get_current_user),
):
    layout = crud.get_layout(db, layout_id)
    if not layout:
        raise HTTPException(status_code=404, detail="التنسيق غير موجود")
    return schemas.StampLayoutOut.model_validate(layout)


@router.get("/", response_model=list[schemas.StampLayoutOut], summary="جلب تنسيقات مادة معينة")
def list_layouts(
    material_id: int,
    db:          Session = Depends(get_db),
    _user:       models.User = Depends(get_current_user),
):
    """جلب كل التنسيقات المرتبطة بمادة محددة"""
    layouts = (
        db.query(models.StampLayout)
        .filter(models.StampLayout.material_id == material_id)
        .all()
    )
    return [schemas.StampLayoutOut.model_validate(l) for l in layouts]


@router.patch("/{layout_id}", response_model=schemas.StampLayoutOut, summary="تعديل تنسيق (Admin فقط)")
def update_layout(
    layout_id: int,
    data:      schemas.StampLayoutUpdate,
    db:        Session = Depends(get_db),
    _admin:    models.User = Depends(require_admin),
):
    layout = crud.update_layout(db, layout_id, data)
    if not layout:
        raise HTTPException(status_code=404, detail="التنسيق غير موجود")
    return schemas.StampLayoutOut.model_validate(layout)


@router.get("/leaks/track", summary="تتبع التسريبات (Admin فقط)")
def track_leak(
    mark_code: str = Query(..., description="كود العلامة المخفية"),
    db:        Session = Depends(get_db),
    _admin:    models.User = Depends(require_admin),
):
    # تنظيف الكود لو المشرف نسخ النص الطويل كله
    # النص بيكون غالباً: PID:50|PAGE:1|60262cb6
    input_code = mark_code.strip()
    
    # 1. محاولة استخراج الـ PID مباشرة (أسرع وأدق طريقة)
    # ندعم الصيغة القديمة (PID:123) والصيغة الجديدة (E-123-XXXX)
    import re
    pid_match = re.search(r"(?:PID:|E-)(\d+)", input_code)
    purchase = None
    
    if pid_match:
        pid = int(pid_match.group(1))
        purchase = crud.get_purchase(db, pid)
    
    # 2. لو فشل استخراج الـ PID، نبحث بالكود الحرفي الكامل
    if not purchase:
        purchase = crud.find_purchase_by_mark_code(db, input_code)

    if not purchase:
        raise HTTPException(status_code=404, detail="لم يُعثر على تطابق لهذا الكود. تأكد من صحة الكود أو أن الملف تم توليده بعد التحديث الأخير.")
    
    buyer = purchase.buyer
    # جلب جميع مشتريات المسرّب لبيان التاريخ والنشاط
    user_purchases, _ = crud.get_user_purchases(db, buyer.id, skip=0, limit=100)
    history = []
    for p in user_purchases:
        history.append({
            "id":                p.id,
            "material_name":     p.material.title if p.material else "محذوف",
            "purchased_at":      p.purchased_at.isoformat(),
            "amount_paid":       float(p.amount_paid),
            "buyer_name_stamp":  p.buyer_name_stamp,
            "buyer_phone_stamp": p.buyer_phone_stamp,
            "watermark_text":    p.watermark_text,
            "doc_name_stamp":    p.doc_name_stamp,
        })

    return {
        "found": True,
        "leak_details": {
            "purchase_id": purchase.id,
            "material_id": purchase.material_id,
            "material_name": purchase.material.title if purchase.material else "محذوف",
            "stamp_name": purchase.buyer_name_stamp,
            "stamp_phone": purchase.buyer_phone_stamp,
            "stamp_watermark": purchase.watermark_text or "لا يوجد",
            "stamp_doc_name": purchase.doc_name_stamp or "لا يوجد",
            "purchased_at": purchase.purchased_at.isoformat()
        },
        "user_details": {
            "id": buyer.id,
            "name": buyer.full_name,
            "email": buyer.email,
            "coins": float(buyer.coins)
        },
        "user_history": history,
        "message": "تم تحديد المسرّب بنجاح وجلب بياناته."
    }
@router.get("/users/{user_id}/activity", summary="جلب نشاط مستخدم معين (للأدمن)")
def get_user_activity_admin(
    user_id:      int,
    db:           Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if current_user.role != models.UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="ليس لديك صلاحية")
        
    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="المستخدم غير موجود")
        
    user_purchases, _ = crud.get_user_purchases(db, user_id, skip=0, limit=100)
    history = []
    for p in user_purchases:
        history.append({
            "id":                p.id,
            "material_name":     p.material.title if p.material else "محذوف",
            "purchased_at":      p.purchased_at.isoformat(),
            "amount_paid":       float(p.amount_paid),
            "buyer_name_stamp":  p.buyer_name_stamp,
            "buyer_phone_stamp": p.buyer_phone_stamp,
            "watermark_text":    p.watermark_text,
            "doc_name_stamp":    p.doc_name_stamp,
        })
        
    return {
        "user_details": {
            "id":    user.id,
            "name":  user.full_name,
            "email": user.email,
            "is_active": user.is_active
        },
        "history": history
    }
