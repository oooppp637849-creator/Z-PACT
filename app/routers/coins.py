# ================================================================
# app/routers/coins.py — نقاط نهاية الكوينز (الرصيد)
# ================================================================

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.auth import get_current_user
from app.database import get_db
from app.models import User, UserRole, TransactionType, Coupon, SpendingLevel, CoinTransaction
from datetime import datetime

router = APIRouter(prefix="/coins", tags=["الكوينز (الرصيد)"])

# ================================================================
# سجل حركات الكوينز للمستخدم الحالي
# ================================================================

@router.get(
    "/history",
    response_model = list[schemas.CoinTransactionOut],
    summary        = "سجل حركات الرصيد",
)
def get_my_coin_history(
    db:           Session = Depends(get_db),
    current_user: User    = Depends(get_current_user),
):
    """إرجاع تاريخ عمليات الشحن والدفع الخاصة بالمستخدم"""
    return crud.get_user_coin_history(db, current_user.id)


# ================================================================
# شحن رصيد لمستخدم (Admin فقط)
# ================================================================

@router.post(
    "/admin/recharge/{user_id}",
    response_model = schemas.UserOut,
    summary        = "شحن رصيد لمستخدم (Admin)",
)
def recharge_user_coins(
    user_id:      int,
    data:         schemas.CoinRecharge,
    db:           Session = Depends(get_db),
    current_user: User    = Depends(get_current_user),
):
    """يسمح للمشرف بإضافة كوينز لرصيد أي مستخدم"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="ليس لديك صلاحية")

    user = crud.update_user_coins(
        db          = db,
        user_id     = user_id,
        amount      = float(data.amount),
        tx_type     = TransactionType.RECHARGE,
        description = data.description,
    )

    if not user:
        raise HTTPException(status_code=404, detail="المستخدم غير موجود")

    # ── مكافأة التسويق (Referral Reward) ──
    if user.referred_by_id and not user.referral_reward_claimed:
        # إضافة 10 كوينز للشخص اللي دعاه
        crud.update_user_coins(
            db          = db,
            user_id     = user.referred_by_id,
            amount      = 10,
            tx_type     = TransactionType.RECHARGE,
            description = f"مكافأة دعوة صديق: {user.full_name}",
        )
        user.referral_reward_claimed = True
        db.commit()

    return user


# ================================================================
# قائمة المستخدمين (Admin فقط) — لإدارة الكوينز
# ================================================================

@router.get(
    "/admin/users",
    response_model = schemas.PaginatedOut,
    summary        = "قائمة المستخدمين (Admin)",
)
def list_users_admin(
    page:         int     = 1,
    per_page:     int     = 50,
    q:            str     = None, # بارامتر البحث
    db:           Session = Depends(get_db),
    current_user: User    = Depends(get_current_user),
):
    """إرجاع قائمة بكل المستخدمين مع إمكانية البحث بالاسم أو الإيميل أو الـ ID"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="ليس لديك صلاحية")

    import math
    skip         = (page - 1) * per_page
    items, total = crud.get_all_users(db, skip=skip, limit=per_page, search=q)

    return schemas.PaginatedOut(
        items       = [schemas.UserOut.model_validate(u) for u in items],
        total       = total,
        page        = page,
        per_page    = per_page,
        total_pages = math.ceil(total / per_page) if total > 0 else 1,
    )


# ================================================================
# القائمة السوداء (Admin فقط)
# ================================================================

@router.get("/admin/blacklist", summary="عرض القائمة السوداء")
def get_blacklist_admin(
    db:           Session = Depends(get_db),
    current_user: User    = Depends(get_current_user),
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="ليس لديك صلاحية")
    return crud.get_blacklist(db)


@router.post("/admin/blacklist", summary="إضافة للقائمة السوداء")
def add_to_blacklist_admin(
    val_type: str, 
    value:    str, 
    reason:   str = None,
    db:           Session = Depends(get_db),
    current_user: User    = Depends(get_current_user),
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="ليس لديك صلاحية")
    return crud.add_to_blacklist(db, val_type, value, reason)


@router.delete("/admin/blacklist/{entry_id}", summary="حذف من القائمة السوداء")
def remove_from_blacklist_admin(
    entry_id:     int,
    db:           Session = Depends(get_db),
    current_user: User    = Depends(get_current_user),
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="ليس لديك صلاحية")
    crud.remove_from_blacklist(db, entry_id)
    return {"status": "success"}


# ================================================================
# إدارة حالة المستخدم (Admin فقط)
# ================================================================

@router.post("/admin/users/{user_id}/toggle-ban", response_model=schemas.UserOut)
def toggle_user_ban(
    user_id:      int,
    db:           Session = Depends(get_db),
    current_user: User    = Depends(get_current_user),
):
    """حظر أو إلغاء حظر مستخدم"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="ليس لديك صلاحية")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="المستخدم غير موجود")
        
    updated = crud.set_user_active_status(db, user_id, not user.is_active)
    return updated


@router.post("/admin/users/{user_id}/make-admin", response_model=schemas.UserOut)
def promote_to_admin(
    user_id:      int,
    db:           Session = Depends(get_db),
    current_user: User    = Depends(get_current_user),
):
    """ترقية مستخدم إلى مدير"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="هذه الصلاحية متاحة للمسؤولين فقط")
        
    updated = crud.set_user_role(db, user_id, UserRole.ADMIN)
    if not updated:
        raise HTTPException(status_code=404, detail="المستخدم غير موجود")
    return updated


@router.post("/redeem-coupon", response_model=schemas.MessageOut)
def redeem_coupon(code: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    coupon = db.query(Coupon).filter(Coupon.code == code).first()
    if not coupon:
        raise HTTPException(status_code=404, detail="كود الكوبون غير صحيح")
    if coupon.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="هذا الكوبون مخصص لحساب آخر ولا يمكن استخدامه هنا")
    if coupon.is_used:
        raise HTTPException(status_code=400, detail="تم استخدام هذا الكوبون مسبقاً")
        
    coupon.is_used = True
    coupon.used_at = datetime.utcnow()
    current_user.coins += coupon.reward_coins
    
    tx = CoinTransaction(
        user_id=current_user.id,
        amount=coupon.reward_coins,
        type=TransactionType.RECHARGE,
        description=f"مكافأة ولاء - كوبون {code}"
    )
    db.add(tx)
    db.commit()
    return {"message": f"تمت إضافة {coupon.reward_coins} كوينز لرصيدك بنجاح"}


@router.get("/admin/spending-levels", response_model=list[schemas.SpendingLevelOut])
def get_spending_levels(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="ليس لديك صلاحية")
    return db.query(SpendingLevel).order_by(SpendingLevel.threshold.asc()).all()

@router.post("/admin/spending-levels", response_model=schemas.SpendingLevelOut)
def create_spending_level(data: schemas.SpendingLevelCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="ليس لديك صلاحية")
    sl = SpendingLevel(threshold=data.threshold, reward_coins=data.reward_coins)
    db.add(sl)
    try:
        db.commit()
        db.refresh(sl)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=400, detail="مستوى الإنفاق هذا موجود مسبقاً أو هناك خطأ")
    return sl

@router.delete("/admin/spending-levels/{level_id}")
def delete_spending_level(level_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="ليس لديك صلاحية")
    sl = db.query(SpendingLevel).filter(SpendingLevel.id == level_id).first()
    if sl:
        db.delete(sl)
        db.commit()
    return {"status": "success"}


# ================================================================
# شحن رصيد ذاتي عبر المحفظة (فودافون كاش / إنستا باي)
# ================================================================

from app.models import WalletTransaction

@router.post(
    "/recharge-wallet",
    summary="شحن رصيد تلقائي عبر المحفظة (فودافون كاش / إنستا باي)",
)
def recharge_wallet(
    transfer_phone: str,
    db:             Session = Depends(get_db),
    current_user:   User    = Depends(get_current_user),
):
    """
    البحث عن تحويل معلق برقم الهاتف (أو اسم صاحب الحساب لـ InstaPay/CIB)
    في جدول wallet_transactions، وإضافة قيمته كوينز لرصيد المستخدم.

    - يقبل أرقام فودافون كاش: 01XXXXXXXXX
    - يقبل أسماء أصحاب حساب InstaPay/CIB كذلك
    """
    from app.logger import logger

    transfer_phone = transfer_phone.strip()
    if not transfer_phone:
        raise HTTPException(status_code=400, detail="يرجى إدخال رقم الهاتف أو اسم المُحوِّل")

    # البحث عن أحدث معاملة معلقة بهذا الرقم/الاسم
    tx = (
        db.query(WalletTransaction)
        .filter(WalletTransaction.sender_phone == transfer_phone)
        .filter(WalletTransaction.status == "pending")
        .order_by(WalletTransaction.transaction_date.asc())
        .with_for_update()
        .first()
    )

    if not tx:
        raise HTTPException(
            status_code=404,
            detail="لم نجد تحويلاً معلقاً من هذا الرقم أو الاسم. "
                   "تأكد من الرقم الذي حوّلت منه أو انتظر دقيقة واحدة وحاول مجدداً."
        )

    # تحديث حالة التحويل → completed
    tx.status = "completed"
    db.commit()

    # إضافة الكوينز للمستخدم
    crud.update_user_coins(
        db          = db,
        user_id     = current_user.id,
        amount      = float(tx.amount),
        tx_type     = TransactionType.RECHARGE,
        description = f"شحن تلقائي من {tx.source or 'المحفظة'} — {transfer_phone}",
    )

    # ── مكافأة التسويق (Referral Reward) ──
    if current_user.referred_by_id and not current_user.referral_reward_claimed:
        # إضافة 10 كوينز للشخص اللي دعاه
        crud.update_user_coins(
            db          = db,
            user_id     = current_user.referred_by_id,
            amount      = 10,
            tx_type     = TransactionType.RECHARGE,
            description = f"مكافأة دعوة صديق: {current_user.full_name}",
        )
        current_user.referral_reward_claimed = True
        db.commit()

    db.refresh(current_user)
    logger.info(
        f"✅ [شحن تلقائي] {current_user.email} شحن {tx.amount} كوين "
        f"من {transfer_phone} (tx_id={tx.id})"
    )

    return {
        "status":      "success",
        "amount_added": float(tx.amount),
        "new_balance":  float(current_user.coins),
        "message":     f"تم إضافة {tx.amount:.0f} كوين لرصيدك بنجاح! 🎉",
    }
