# ================================================================
# app/auth.py — نظام التوثيق (JWT)
#
# المسؤوليات:
#   - إنشاء JWT tokens بعد تسجيل الدخول
#   - التحقق من الـ token في كل Request محمي
#   - Dependencies جاهزة للاستخدام في الـ routers:
#       get_current_user  → أي مستخدم مسجل دخول
#       require_admin     → Admin فقط
# ================================================================

import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app import crud, models
from app.database import get_db

from app.config import settings

# -----------------------------------------------------------
# إعدادات الـ JWT — تأتي من المتغيرات البيئية عبر config.py
# -----------------------------------------------------------
SECRET_KEY = settings.SECRET_KEY
ALGORITHM  = settings.ALGORITHM
TOKEN_EXPIRE_H = settings.TOKEN_EXPIRE_H

if SECRET_KEY == "change-me-in-production-please":
    from app.logger import logger
    logger.warning("⚠️ [Security Warning] Using default JWT_SECRET_KEY. Please set a strong one in environment variables.")

# HTTPBearer بيقرأ الـ token من header: Authorization: Bearer <token>
bearer_scheme = HTTPBearer()


# ================================================================
# إنشاء وفك الـ JWT
# ================================================================

def create_access_token(user_id: int, role: str) -> str:
    """
    إنشاء JWT token جديد.
    الـ payload فيه:
      sub  → user_id (الـ subject)
      role → دور المستخدم
      exp  → وقت انتهاء الصلاحية
    """
    payload = {
        "sub":  str(user_id),
        "role": role,
        "exp":  datetime.utcnow() + timedelta(hours=TOKEN_EXPIRE_H),
        "iat":  datetime.utcnow(),  # وقت الإنشاء
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> Optional[dict]:
    """
    فك تشفير الـ JWT والتحقق من صلاحيته.
    بيرجع الـ payload لو صحيح، أو None لو منتهي أو تالف.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


# ================================================================
# FastAPI Dependencies — بتُحقن في الـ endpoints
# ================================================================

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db:          Session                      = Depends(get_db),
) -> models.User:
    """
    Dependency — يتحقق من الـ JWT ويرجع المستخدم الحالي.
    يُستخدم في كل endpoint يحتاج تسجيل دخول:
        user: User = Depends(get_current_user)
    """
    token   = credentials.credentials
    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail      = "التوكن غير صالح أو منتهي الصلاحية",
            headers     = {"WWW-Authenticate": "Bearer"},
        )

    user_id = int(payload.get("sub", 0))
    user    = crud.get_user_by_id(db, user_id)

    if not user or not user.is_active:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail      = "المستخدم غير موجود أو محظور",
        )

    return user


def require_admin(current_user: models.User = Depends(get_current_user)) -> models.User:
    """
    Dependency — يتحقق إن المستخدم Admin.
    يُستخدم في endpoints إدارة المتجر:
        admin: User = Depends(require_admin)
    """
    if current_user.role != models.UserRole.ADMIN:
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail      = "هذه العملية متاحة للمديرين فقط",
        )
    return current_user


async def get_current_user_ws(token: str) -> Optional[models.User]:
    """
    Dependency — يتحقق من الـ JWT ويرجع المستخدم في حالة الـ WebSocket.
    """
    payload = decode_access_token(token)
    if not payload:
        return None
        
    user_id = int(payload.get("sub", 0))
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        user = crud.get_user_by_id(db, user_id)
        if not user or not user.is_active:
            return None
        return user
    finally:
        db.close()
