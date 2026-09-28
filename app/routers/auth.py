# ================================================================
# app/routers/auth.py — نقاط نهاية التوثيق
#
# Endpoints:
#   POST /auth/register  - تسجيل مستخدم جديد
#   POST /auth/login     - تسجيل الدخول والحصول على JWT
#   GET  /auth/me        - بيانات المستخدم الحالي
# ================================================================

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app import crud, schemas
from app.auth import create_access_token, get_current_user
from app.database import get_db
from app.models import User, UserRole

router = APIRouter(prefix="/auth", tags=["التوثيق"])


@router.post(
    "/register",
    response_model = schemas.UserOut,
    status_code    = status.HTTP_201_CREATED,
    summary        = "تسجيل مستخدم جديد (Customer)",
)
def register(data: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    تسجيل مستخدم جديد بدور Customer.
    لو الإيميل موجود مسبقاً، بيرجع خطأ 400.
    """
    # التحقق إن الإيميل مش مستخدم
    existing = crud.get_user_by_email(db, data.email)
    if existing:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail      = "الإيميل ده مسجل مسبقاً",
        )

    # التحقق من كود الدعوة (اختياري)
    if data.referral_code:
        inviter = db.query(User).filter(User.referral_code == data.referral_code).first()
        if not inviter:
             raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail      = "كود الدعوة غير صحيح",
            )

    # إنشاء المستخدم بدور Customer دايماً من هنا
    user = crud.create_user(db, data, role=UserRole.CUSTOMER)
    return user



@router.post(
    "/login",
    response_model = schemas.TokenOut,
    summary        = "تسجيل الدخول",
)
def login(request: Request, data: schemas.UserLogin, db: Session = Depends(get_db)):
    """
    تسجيل الدخول بالإيميل وكلمة المرور + حماية الأجهزة.
    """
    user = crud.authenticate_user(db, data.email, data.password)

    if not user:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail      = "بيانات الدخول غير صحيحة",
        )

    # ── حماية الأجهزة (Device Locking) ──
    # الأدمن مسموح له بـ 5 أجهزة، الطالب بجهازين فقط
    limit = 5 if user.role == UserRole.ADMIN else 2
    
    devices = crud.get_user_devices(db, user.id)
    existing_device = next((d for d in devices if d.device_id == data.device_id), None)
    
    if existing_device:
        if existing_device.is_blocked:
            raise HTTPException(
                status_code=403,
                detail="⚠️ هذا الجهاز محظور من دخول المنصة. يرجى مراجعة الإدارة."
            )
        # تحديث بيانات الدخول الأخير
        existing_device.last_login = datetime.utcnow()
        existing_device.last_ip = request.client.host if request.client else None
        db.commit()
    else:
        # جهاز جديد
        if len(devices) >= limit:
            raise HTTPException(
                status_code=403,
                detail=f"⚠️ عذراً، لقد وصلت للحد الأقصى للأجهزة ({limit} أجهزة). "
                       f"يرجى تسجيل الدخول من أجهزتك السابقة أو التواصل مع الإدارة لطلب إعادة تعيين."
            )
        
        # تسجيل الجهاز الجديد
        crud.register_user_device(
            db=db,
            user_id=user.id,
            device_id=data.device_id,
            user_agent=request.headers.get("User-Agent"),
            ip=request.client.host if request.client else None
        )

    token = create_access_token(user_id=user.id, role=user.role.value)

    return schemas.TokenOut(
        access_token = token,
        user         = schemas.UserOut.model_validate(user),
    )


@router.get(
    "/me",
    response_model = schemas.UserOut,
    summary        = "بيانات المستخدم الحالي",
)
def get_me(current_user: User = Depends(get_current_user)):
    """
    إرجاع بيانات المستخدم المسجل دخوله حالياً.
    يحتاج JWT token في الـ Authorization header.
    """
    return current_user
