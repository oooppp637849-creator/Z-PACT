# ================================================================
# app/routers/admin_tools.py — أدوات الإدارة المتقدمة
# ================================================================

import os
import shutil
import zipfile
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app import schemas
from app.auth import get_current_user
from app.database import get_db
from app.models import User, UserRole
from app.config import settings

router = APIRouter(prefix="/admin-tools", tags=["أدوات الإدارة"])

@router.get("/download-db", summary="تحميل قاعدة البيانات (إدمن فقط)")
def download_database(current_user: User = Depends(get_current_user)):
    """
    يسمح بتحميل ملف قاعدة البيانات بالكامل.
    يجب أن يكون المستخدم Admin.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="ليس لديك صلاحية للقيام بهذا الإجراء")

    # استخدام المسار المحسوب بدقة من الإعدادات
    db_path = settings.DATABASE_PATH
    target_filename = os.path.basename(db_path)
            
    if not os.path.exists(db_path):
        # محاولة أخيرة للبحث لو المسار المطلق فشل (Railway volumes)
        found = False
        search_paths = [settings.BASE_DIR, "/app", "/data", "/.data"]
        for sp in search_paths:
            if os.path.exists(sp):
                for root, dirs, files in os.walk(sp):
                    if target_filename in files:
                        db_path = os.path.join(root, target_filename)
                        found = True
                        break
            if found: break
            
    if not os.path.exists(db_path):
        raise HTTPException(status_code=404, detail=f"لم يتم العثور على قاعدة البيانات. آخر مسار فحصناه: {db_path}")

    return FileResponse(
        path=db_path,
        filename=f"backup_{target_filename}",
        media_type="application/x-sqlite3"
    )

@router.get("/system-info", summary="معلومات النظام")
def get_system_info(current_user: User = Depends(get_current_user)):
    """إحصائيات سريعة عن النظام"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="ليس لديك صلاحية")
        
    actual = settings.DATABASE_PATH
    
    if not os.path.exists(actual):
        target_filename = os.path.basename(actual)
        search_paths = [settings.BASE_DIR, "/app", "/data", "/.data"]
        for sp in search_paths:
            if os.path.exists(sp):
                for root, dirs, files in os.walk(sp):
                    if target_filename in files:
                        actual = os.path.join(root, target_filename)
                        break
            if os.path.exists(actual): break

    return {
        "os": os.name,
        "base_dir": settings.BASE_DIR,
        "database_url": settings.DATABASE_URL,
        "resolved_db_path": actual,
        "db_exists": os.path.exists(actual),
        "database_type": "SQLite"
    }

@router.post("/broadcast", summary="إرسال إشعار للنظام")
def broadcast_notification(data: schemas.AdminBroadcast, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """إرسال إشعار لمستخدم معين أو للجميع"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="ليس لديك صلاحية")
        
    from app.models import Notification
    new_notif = Notification(
        user_id=data.user_id,
        title=data.title,
        message=data.message
    )
    db.add(new_notif)
    db.commit()
    return {"message": "تم إرسال الإشعار بنجاح"}

@router.post("/restore-db", summary="استعادة قاعدة البيانات (إدمن فقط)")
def restore_database(file: UploadFile = File(...), current_user: User = Depends(get_current_user)):
    """
    استبدال قاعدة البيانات الحالية بملف SQLite مرفوع.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="ليس لديك صلاحية للقيام بهذا الإجراء")

    filename = file.filename
    if not (filename.endswith(".db") or filename.endswith(".sqlite")):
        raise HTTPException(status_code=400, detail="يجب رفع ملف قاعدة بيانات SQLite (.db أو .sqlite) فقط")

    db_path = settings.DATABASE_PATH
    
    # 1. إغلاق اتصالات قاعدة البيانات المفتوحة في SQLAlchemy
    from app.database import engine
    engine.dispose()

    try:
        # 2. حذف الملف القديم وكتابة الجديد
        if os.path.exists(db_path):
            os.remove(db_path)
            
        with open(db_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
            
        # 3. إعادة تهيئة الجداول وترقيع الأعمدة الناقصة
        from app.database import create_tables
        create_tables()
        
        return {"message": "تم استعادة قاعدة البيانات بنجاح وإعادة بناء الجداول وتفعيلها."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"حدث خطأ أثناء استعادة قاعدة البيانات: {str(e)}")

@router.post("/restore-materials", summary="استيراد الملفات الأصلية كـ ZIP (إدمن فقط)")
def restore_materials(file: UploadFile = File(...), current_user: User = Depends(get_current_user)):
    """
    استيراد مذكرات PDF الأصلية من ملف ZIP مضغوط واستخراجها في originals.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="ليس لديك صلاحية للقيام بهذا الإجراء")

    if not file.filename.endswith(".zip"):
        raise HTTPException(status_code=400, detail="يجب رفع ملف مضغوط بصيغة ZIP (.zip) فقط")

    originals_dir = os.path.join(settings.STORAGE_DIR, "originals")
    os.makedirs(originals_dir, exist_ok=True)

    # حفظ ملف ZIP مؤقتاً واستخراجه
    import tempfile
    with tempfile.TemporaryDirectory() as tmp_dir:
        zip_path = os.path.join(tmp_dir, "materials.zip")
        with open(zip_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(originals_dir)
            return {"message": "تم استخراج واستيراد ملفات المذكرات الأصلية بنجاح."}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"حدث خطأ أثناء فك ضغط واستعادة الملفات: {str(e)}")


@router.post("/merge-db", summary="الدمج الذكي لقواعد البيانات (إدمن فقط)")
def smart_merge_database(file: UploadFile = File(...), current_user: User = Depends(get_current_user)):
    """
    يقوم بدمج قاعدة البيانات المرفوعة مع الحالية بناءً على معيار 'السجل الأغنى' (الأكثر امتلاءً بالبيانات).
    """
    import sqlite3
    import tempfile
    
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="ليس لديك صلاحية للقيام بهذا الإجراء")

    if not (file.filename.endswith(".db") or file.filename.endswith(".sqlite") or file.filename.endswith(".sqlite3")):
        raise HTTPException(status_code=400, detail="يجب رفع ملف SQLite فقط")

    # 1. حفظ الملف المرفوع في مسار مؤقت
    with tempfile.NamedTemporaryFile(delete=False, suffix=".sqlite3") as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    db_path = settings.DATABASE_PATH
    
    summary = {"tables_processed": 0, "records_added": 0, "records_updated": 0, "records_skipped": 0}
    
    try:
        # اتصال بالقاعدة الحالية
        conn_main = sqlite3.connect(db_path)
        conn_main.row_factory = sqlite3.Row
        cur_main = conn_main.cursor()
        
        # اتصال بالقاعدة المرفوعة
        conn_up = sqlite3.connect(tmp_path)
        conn_up.row_factory = sqlite3.Row
        cur_up = conn_up.cursor()
        
        # استخراج الجداول من المرفوعة
        cur_up.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        raw_tables = [row['name'] for row in cur_up.fetchall()]
        import re
        tables = [t for t in raw_tables if re.match(r'^[a-zA-Z0-9_]+$', t)]
        
        for table in tables:
            summary["tables_processed"] += 1
            
            # جلب كل السجلات من الجدول المرفوع
            try:
                cur_up.execute(f'SELECT * FROM "{table}"')
                up_records = cur_up.fetchall()
            except sqlite3.Error:
                continue # تخطي في حالة مشكلة بالجدول
                
            if not up_records:
                continue
                
            # جلب أعمدة الجدول وفحص أمان أسمائها
            raw_columns = list(up_records[0].keys())
            columns = [c for c in raw_columns if re.match(r'^[a-zA-Z0-9_]+$', c)]
            if not columns or len(columns) != len(raw_columns):
                continue
            
            for up_row in up_records:
                try:
                    # محاولة البحث عن السجل المطابق في الأساسي عبر الـ id
                    if 'id' in columns:
                        cur_main.execute(f"SELECT * FROM {table} WHERE id=?", (up_row['id'],))
                    else:
                        continue # لا يمكن الدمج بدون معرف
                        
                    main_row = cur_main.fetchone()
                    
                    if not main_row:
                        # إضافة جديدة (Insert)
                        placeholders = ",".join(["?"] * len(columns))
                        cols_str = ",".join(columns)
                        cur_main.execute(f"INSERT INTO {table} ({cols_str}) VALUES ({placeholders})", tuple(up_row))
                        summary["records_added"] += 1
                    else:
                        # موجود مسبقاً -> نقارن مين أغنى بالبيانات (Richest Record Heuristic)
                        def score_row(r):
                            score = 0
                            for k in columns:
                                val = r[k]
                                if val is not None and str(val).strip() != "" and str(val).strip() != "0":
                                    score += 1
                            return score
                            
                        score_up = score_row(up_row)
                        score_main = score_row(main_row)
                        
                        if score_up > score_main:
                            # تحديث بالبيانات الأغنى (Update)
                            set_clause = ", ".join([f"{c}=?" for c in columns if c != 'id'])
                            values = [up_row[c] for c in columns if c != 'id']
                            values.append(up_row['id'])
                            cur_main.execute(f"UPDATE {table} SET {set_clause} WHERE id=?", tuple(values))
                            summary["records_updated"] += 1
                        else:
                            summary["records_skipped"] += 1
                except sqlite3.Error as e:
                    print(f"Skipping row in {table} due to error: {e}")
                    summary["records_skipped"] += 1
                    continue
                    
        conn_main.commit()
        
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"خطأ أثناء دمج القواعد: {e}")
    finally:
        if 'conn_main' in locals(): conn_main.close()
        if 'conn_up' in locals(): conn_up.close()
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
            
    return {"message": "تم الدمج بنجاح", "summary": summary}


@router.post("/sync-github", summary="مزامنة ورفع المشروع تلقائياً إلى GitHub")
def sync_github(current_user: User = Depends(get_current_user)):
    """تنظيف ملفات الاختبار ورفع المشروع بضغطة واحدة إلى GitHub"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="ليس لديك صلاحية للقيام بهذا الإجراء")

    import subprocess
    import sys
    script_path = os.path.join(settings.BASE_DIR, "push_to_github.py")
    if not os.path.exists(script_path):
        raise HTTPException(status_code=404, detail="لم يتم العثور على سكريبت الرفع push_to_github.py")

    res = subprocess.run([sys.executable, script_path], capture_output=True, text=True)
    if res.returncode == 0:
        return {"status": "success", "message": "تم تنظيف الملفات ورفع المشروع بنجاح إلى GitHub!", "repo": "https://github.com/oooppp637849-creator/Z-PACT"}
    else:
        return {"status": "error", "message": "حدث خطأ أثناء الرفع", "details": res.stderr[-300:] or res.stdout[-300:]}

