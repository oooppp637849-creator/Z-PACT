# ================================================================
# app/routers/jobs.py — نظام الوظائف الخلفية (Background Jobs)
#
# يتيح للمستخدم بدء عملية توليد PDF في الخلفية والعودة للصفحة الرئيسية،
# ثم متابعة حالة العملية عبر polling حتى يظهر رابط التحميل.
#
# الـ Endpoints:
#   GET  /jobs/{job_id}          → حالة الوظيفة (processing / done / error)
#   GET  /jobs/{job_id}/download → تحميل الملف الجاهز
# ================================================================

import os
import time
import threading
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.auth import get_current_user, require_admin
from app.database import get_db, SessionLocal
from app.models import User, BackgroundJob, UserRole
from app import crud

router = APIRouter(prefix="/jobs", tags=["الوظائف الخلفية"])

# ----------------------------------------------------------------
# مخزن الوظائف في الذاكرة (بسيط وكافٍ للاستخدام الحالي)
# ----------------------------------------------------------------
# كل وظيفة لها:
#   status: "processing" | "done" | "error"
#   file_path: المسار للملف الجاهز (لو done)
#   error: رسالة الخطأ (لو error)
#   label: اسم الملف للعرض
#   created_at: وقت الإنشاء للتنظيف التلقائي

_jobs: dict[str, dict] = {}
_jobs_lock = threading.Lock()


def create_job(job_id: str, user_id: int, label: str = "ملف") -> None:
    """إنشاء وظيفة جديدة في الذاكرة وفي قاعدة البيانات"""
    with _jobs_lock:
        _jobs[job_id] = {
            "status":     "processing",
            "file_path":  None,
            "error":      None,
            "label":      label,
            "created_at": time.time(),
            "user_id":    user_id
        }
    
    # حفظ في قاعدة البيانات (في thread منفصل لتجنب تأخير الـ Response)
    def _save_to_db():
        with SessionLocal() as db:
            crud.create_background_job(db, user_id, job_id, label)
    threading.Thread(target=_save_to_db).start()


def complete_job(job_id: str, file_path: str) -> None:
    """تعيين الوظيفة كمكتملة وتحديث قاعدة البيانات"""
    with _jobs_lock:
        if job_id in _jobs:
            _jobs[job_id]["status"]    = "done"
            _jobs[job_id]["file_path"] = file_path

    with SessionLocal() as db:
        crud.update_background_job(db, job_id, "done", output_path=file_path)


def fail_job(job_id: str, error: str) -> None:
    """تعيين الوظيفة كفاشلة وتحديث قاعدة البيانات"""
    with _jobs_lock:
        if job_id in _jobs:
            _jobs[job_id]["status"] = "error"
            _jobs[job_id]["error"]  = error

    with SessionLocal() as db:
        crud.update_background_job(db, job_id, "failed", error=error)


def cleanup_old_jobs() -> None:
    """تنظيف الوظائف القديمة (أكثر من ساعة)"""
    now = time.time()
    with _jobs_lock:
        old_ids = [
            jid for jid, job in _jobs.items()
            if now - job["created_at"] > 3600
        ]
        for jid in old_ids:
            # حذف الملف المؤقت لو موجود
            fp = _jobs[jid].get("file_path")
            if fp and os.path.exists(fp):
                try:
                    os.remove(fp)
                except Exception:
                    pass
            del _jobs[jid]


# ----------------------------------------------------------------
# Endpoints
# ----------------------------------------------------------------

@router.get(
    "/recent",
    summary = "جلب آخر الوظائف للمستخدم",
)
def get_recent_jobs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """جلب آخر 10 وظائف (للمستخدم العادي) أو كل الوظائف (للمدير)"""
    if current_user.role == UserRole.ADMIN:
        # المدير يشوف آخر 20 وظيفة في السيستم كله
        jobs = db.query(BackgroundJob).order_by(BackgroundJob.created_at.desc()).limit(20).all()
    else:
        # المستخدم العادي يشوف حاجته بس
        jobs = crud.get_user_background_jobs(db, current_user.id, limit=10)
    return [
        {
            "job_id": j.job_id,
            "status": j.status,
            "label":  j.label,
            "download_url": f"/api/jobs/{j.job_id}/download" if j.status == "done" else None,
            "error": j.error_message if j.status == "failed" else None,
            "created_at": j.created_at
        }
        for j in jobs
    ]


@router.get(
    "/{job_id}",
    summary = "متابعة حالة وظيفة توليد PDF",
)
def get_job_status(
    job_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    إرجاع حالة الوظيفة:
      - processing: لا تزال تعمل
      - done:       جاهزة للتحميل
      - error:      فشلت
    """
    cleanup_old_jobs()

    with _jobs_lock:
        job = _jobs.get(job_id)

    if not job:
        # لو مش في الذاكرة، نشوف في قاعدة البيانات
        db_job = crud.get_background_job_by_id(db, job_id)
        if not db_job:
            raise HTTPException(status_code=404, detail="الوظيفة غير موجودة")
        
        job = {
            "status": "done" if db_job.status == "done" else ("error" if db_job.status == "failed" else "processing"),
            "label": db_job.label,
            "file_path": db_job.output_path,
            "error": db_job.error_message
        }

    response = {
        "job_id": job_id,
        "status": job["status"],
        "label":  job["label"],
    }

    if job["status"] == "done":
        response["download_url"] = f"/api/jobs/{job_id}/download"

    if job["status"] == "error":
        response["error"] = job.get("error")

    return response


@router.get(
    "/{job_id}/download",
    summary = "تحميل ملف PDF الجاهز",
)
def download_job_file(job_id: str):
    """
    تحميل الملف الجاهز. يُحذف الملف من السيرفر بعد 10 دقائق تلقائياً.
    الوصول متاح عبر معرف الوظيفة (UUID) مباشرة للسماح بالتحميل من روابط الـ HTML.
    """
    with _jobs_lock:
        job = _jobs.get(job_id)

    if not job:
        # لو مش في الذاكرة، نشوف في قاعدة البيانات
        with SessionLocal() as db:
            db_job = crud.get_background_job_by_id(db, job_id)
            if not db_job:
                raise HTTPException(status_code=404, detail="الوظيفة غير موجودة أو انتهت صلاحيتها")
            
            job = {
                "status": "done" if db_job.status == "done" else ("error" if db_job.status == "failed" else "processing"),
                "file_path": db_job.output_path
            }

    if job["status"] != "done":
        raise HTTPException(status_code=400, detail="الملف لم يكتمل بعد")

    file_path = job["file_path"]
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="الملف غير موجود على السيرفر")

    filename = os.path.basename(file_path)

    # جدولة حذف الملف بعد 10 دقائق
    def _delayed_delete():
        time.sleep(600)
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception:
            pass
        with _jobs_lock:
            if job_id in _jobs:
                del _jobs[job_id]

    t = threading.Thread(target=_delayed_delete, daemon=True)
    t.start()

    return FileResponse(
        path        = file_path,
        media_type  = "application/pdf",
        filename    = filename,
        headers     = {"Content-Disposition": f"attachment; filename={filename}"},
    )
