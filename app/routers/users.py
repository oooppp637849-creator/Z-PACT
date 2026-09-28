import os
import shutil
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session

from app import schemas
from app.auth import get_current_user
from app.database import get_db
from app.models import User, UserAuditLog, Notification, UserRole
from app.crud import hash_password
from app.config import settings
from app import models
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["المستخدمين"])

def get_password_hash(password: str) -> str:
    return hash_password(password)


@router.put("/me", response_model=schemas.UserOut)
def update_user_me(data: schemas.UserUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """تحديث بيانات المستخدم وحفظ السجل"""
    old_data = {
        "full_name": current_user.full_name,
        "email": current_user.email,
        "phone": current_user.phone
    }
    
    # Check email uniqueness if changed
    if data.email and data.email != current_user.email:
        existing = db.query(User).filter(User.email == data.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="هذا الإيميل مستخدم مسبقاً")
        current_user.email = data.email
        
    if data.full_name:
        current_user.full_name = data.full_name
    if data.phone:
        current_user.phone = data.phone
    if data.password:
        current_user.password_hash = get_password_hash(data.password)

    new_data = {
        "full_name": current_user.full_name,
        "email": current_user.email,
        "phone": current_user.phone
    }

    # Log changes if there are any profile changes (excluding password)
    if old_data != new_data:
        audit_log = UserAuditLog(
            user_id=current_user.id,
            action="UPDATE_PROFILE",
            old_data=old_data,
            new_data=new_data
        )
        db.add(audit_log)

    db.commit()
    db.refresh(current_user)
    return current_user


@router.get("/me/preferences")
def get_user_preferences(current_user: User = Depends(get_current_user)):
    """جلب إعدادات المستخدم"""
    return current_user.preferences or {"theme": "dark", "chat_visible": True, "notifications": True}

@router.patch("/me/preferences")
def update_user_preferences(data: schemas.UserPreferencesUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """تحديث إعدادات المستخدم جزئياً"""
    current_prefs = dict(current_user.preferences or {"theme": "dark", "chat_visible": True, "notifications": True})
    current_prefs.update(data.preferences)
    current_user.preferences = current_prefs
    
    from sqlalchemy.orm.attributes import flag_modified
    flag_modified(current_user, "preferences")
    
    db.commit()
    return {"message": "تم تحديث الإعدادات بنجاح", "preferences": current_prefs}



ALLOWED_IMAGE_EXTS = {"png", "jpg", "jpeg", "webp", "gif"}
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5 MB

@router.post("/me/avatar", response_model=schemas.MessageOut)
def upload_avatar(file: UploadFile = File(...), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """رفع صورة الملف الشخصي بأمان وفحص الصيغة والحجم لمنع الهجمات"""
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="يجب رفع صورة صالحة فقط")
    
    ext = file.filename.split(".")[-1].lower() if file.filename and "." in file.filename else "png"
    if ext not in ALLOWED_IMAGE_EXTS:
        raise HTTPException(status_code=400, detail="صيغة الصورة غير مدعومة. الصيغ المسموحة: PNG, JPG, WEBP, GIF")
    
    # التحقق من حجم الصورة
    file_bytes = file.file.read(MAX_IMAGE_SIZE + 1)
    if len(file_bytes) > MAX_IMAGE_SIZE:
        raise HTTPException(status_code=400, detail="حجم الصورة يجب ألا يتجاوز 5 ميجابايت")
    file.file.seek(0)

    upload_dir = os.path.join(settings.STORAGE_DIR, "avatars")
    os.makedirs(upload_dir, exist_ok=True)
    
    filename = f"avatar_{current_user.id}_{int(datetime.now().timestamp())}.{ext}"
    file_path = os.path.join(upload_dir, filename)
    
    # حذف الصورة القديمة لمنع تراكم الملفات غير المستخدمة
    if current_user.profile_picture_path:
        old_path_abs = os.path.join(settings.BASE_DIR, current_user.profile_picture_path.lstrip("/"))
        if os.path.exists(old_path_abs) and os.path.isfile(old_path_abs):
            try:
                os.remove(old_path_abs)
            except Exception as e:
                logger.error(f"Failed to delete old avatar: {e}")

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    base = settings.BASE_DIR.replace("\\", "/").rstrip("/")
    relative_path = file_path.replace("\\", "/").replace(base + "/", "", 1)
    current_user.profile_picture_path = relative_path
    db.commit()
    
    return {"message": "تم تحديث الصورة بنجاح"}


@router.post("/me/watermark-logo", response_model=schemas.MessageOut)
def upload_watermark_logo(file: UploadFile = File(...), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """رفع شعار العلامة المائية الخاص بالمدرس وإزالة الخلفية البيضاء تلقائياً بأمان"""
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="يجب رفع صورة صالحة فقط")
    
    ext = file.filename.split(".")[-1].lower() if file.filename and "." in file.filename else "png"
    if ext not in ALLOWED_IMAGE_EXTS:
        raise HTTPException(status_code=400, detail="صيغة الصورة غير مدعومة. الصيغ المسموحة: PNG, JPG, WEBP, GIF")

    file_bytes = file.file.read(MAX_IMAGE_SIZE + 1)
    if len(file_bytes) > MAX_IMAGE_SIZE:
        raise HTTPException(status_code=400, detail="حجم الشعار يجب ألا يتجاوز 5 ميجابايت")
    file.file.seek(0)
    
    upload_dir = os.path.join(settings.STORAGE_DIR, "logos")
    os.makedirs(upload_dir, exist_ok=True)
    
    # سنحفظ الملف دائماً بصيغة png لأنها تدعم الشفافية
    filename = f"logo_{current_user.id}_{int(datetime.now().timestamp())}.png"
    file_path = os.path.join(upload_dir, filename)
    
    # حذف اللوجو القديم لمنع تراكم الملفات غير المستخدمة
    if current_user.watermark_logo_path:
        old_path_abs = os.path.join(settings.BASE_DIR, current_user.watermark_logo_path.lstrip("/"))
        if os.path.exists(old_path_abs) and os.path.isfile(old_path_abs):
            try:
                if "assets/logo.png" not in current_user.watermark_logo_path:
                    os.remove(old_path_abs)
            except Exception as e:
                logger.error(f"Failed to delete old watermark logo: {e}")

    try:
        from PIL import Image
        import io
        
        # قراءة محتويات الملف المرفوع
        contents = file.file.read()
        img = Image.open(io.BytesIO(contents))
        img = img.convert("RGBA")
        
        # إزالة الخلفية البيضاء المتصلة بالحدود باستخدام flood-fill عبر مسح كامل حدود الصورة
        datas = img.getdata()
        new_data = []
        for item in datas:
            if item[0] > 210 and item[1] > 210 and item[2] > 210:
                new_data.append((255, 255, 255, 0))
            else:
                new_data.append(item)
        img.putdata(new_data)
        
        # حفظ الصورة بصيغة PNG
        img.save(file_path, "PNG")
    except Exception as e:
        logger.error(f"Error processing logo background removal: {e}")
        raise HTTPException(status_code=400, detail="فشل معالجة الصورة وإزالة الخلفية البيضاء")
        
    base = settings.BASE_DIR.replace("\\", "/").rstrip("/")
    relative_path = file_path.replace("\\", "/").replace(base + "/", "", 1)
    current_user.watermark_logo_path = relative_path
    db.commit()
    
    return {"message": "تم تحديث شعار العلامة المائية بنجاح"}

@router.get("/notifications", response_model=List[schemas.NotificationOut])
def get_notifications(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """جلب الإشعارات للمستخدم والإشعارات العامة"""
    notifications = db.query(Notification).filter(
        (Notification.user_id == current_user.id) | (Notification.user_id == None)
    ).order_by(Notification.created_at.desc()).limit(50).all()
    return notifications

@router.post("/notifications/read", response_model=schemas.MessageOut)
def mark_notifications_read(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """تحديد إشعارات المستخدم كمقروءة"""
    db.query(Notification).filter(Notification.user_id == current_user.id, Notification.is_read == False).update({"is_read": True})
    db.commit()
    return {"message": "تم تحديث الإشعارات"}


@router.put("/admin/{user_id}/password", response_model=schemas.MessageOut)
def admin_reset_password(user_id: int, new_password: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """تغيير كلمة مرور أي مستخدم (للإدمن الأساسي فقط)"""
    if current_user.id != 1:
        raise HTTPException(status_code=403, detail="هذه الصلاحية متاحة للإدمن الأساسي فقط")
        
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="المستخدم غير موجود")
        
    user.password_hash = get_password_hash(new_password)
    db.commit()
    return {"message": "تم تغيير كلمة المرور بنجاح"}


@router.delete("/admin/{user_id}", response_model=schemas.MessageOut)
def admin_delete_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """حذف مستخدم (للإدمن الأساسي فقط)"""
    if current_user.id != 1:
        raise HTTPException(status_code=403, detail="هذه الصلاحية متاحة للإدمن الأساسي فقط")
        
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="المستخدم غير موجود")
        
    # We can perform a soft delete or a hard delete. Let's do hard delete for now.
    db.delete(user)
    db.commit()
    return {"message": "تم حذف المستخدم بنجاح"}


@router.get("/admin/{user_id}/audit", response_model=List[schemas.UserAuditLogOut])
def admin_get_user_audit(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """جلب سجل التعديلات الخاصة بمستخدم معين"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="ليس لديك صلاحية")
        
    logs = db.query(UserAuditLog).filter(UserAuditLog.user_id == user_id).order_by(UserAuditLog.created_at.desc()).all()
    return logs


# ── إدارة الأجهزة (Device Management) ──

@router.get("/admin/{user_id}/devices", response_model=List[schemas.UserDeviceOut])
def admin_get_user_devices(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """عرض الأجهزة المسجلة للمستخدم"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="ليس لديك صلاحية")
    return db.query(models.UserDevice).filter(models.UserDevice.user_id == user_id).all()

@router.delete("/admin/{user_id}/devices", response_model=schemas.MessageOut)
def admin_reset_user_devices(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """حذف كل الأجهزة المسجلة (إعادة تعيين)"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="ليس لديك صلاحية")
    
    from app import crud
    crud.delete_all_user_devices(db, user_id)
    return {"message": "تمت إعادة تعيين الأجهزة بنجاح. يمكن للمستخدم الآن الدخول من أجهزة جديدة."}

@router.post("/admin/devices/{device_record_id}/toggle-block", response_model=schemas.MessageOut)
def admin_toggle_device_block(device_record_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """حظر أو إلغاء حظر جهاز معين"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="ليس لديك صلاحية")
    
    device = db.query(models.UserDevice).filter(models.UserDevice.id == device_record_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="سجل الجهاز غير موجود")
    
    device.is_blocked = not device.is_blocked
    db.commit()
    
    status_str = "محظور" if device.is_blocked else "نشط"
    return {"message": f"تم تغيير حالة الجهاز إلى {status_str}"}
