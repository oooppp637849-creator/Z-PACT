# ================================================================
# app/routers/materials.py — نقاط نهاية الملفات (Materials)
#
# الـ Endpoints:
#   GET    /materials/           → قائمة الملفات المنشورة (للجميع)
#   POST   /materials/           → رفع ملف جديد (Admin فقط)
#   GET    /materials/{id}       → تفاصيل ملف معين
#   PATCH  /materials/{id}       → تعديل بيانات ملف (Admin فقط)
#   DELETE /materials/{id}       → حذف ملف (Admin فقط)
#   POST   /materials/{id}/preview-token → طلب توكن معاينة
#   GET    /materials/preview    → معاينة آمنة بالتوكن (Binary Blob)
# ================================================================

import asyncio
import base64
import math
import os
import shutil
import uuid
from datetime import datetime
from typing import Optional

from fastapi import (APIRouter, Depends, File, Form, HTTPException,
                     Query, UploadFile, status, BackgroundTasks)
from fastapi.responses import FileResponse, StreamingResponse, JSONResponse
from sqlalchemy.orm import Session

import fitz  # PyMuPDF — لقراءة عدد صفحات الـ PDF
from app import crud, schemas, models
from app.auth import decode_access_token, get_current_user, require_admin
from app.database import get_db
from app.models import User, Review, Purchase, PurchaseStatus
from app.stamper import run_test_stamp
from app.routers import jobs as jobs_store
from app.config import settings
from app.logger import logger

router = APIRouter(prefix="/materials", tags=["الملفات"])

# مجلد حفظ الملفات المرفوعة على السيرفر
UPLOAD_DIR = os.path.join(settings.STORAGE_DIR, "originals")
os.makedirs(UPLOAD_DIR, exist_ok=True)

COVERS_DIR = os.path.join(settings.STORAGE_DIR, "covers")
os.makedirs(COVERS_DIR, exist_ok=True)

FRAMES_DIR = os.path.join(settings.STORAGE_DIR, "frames")
os.makedirs(FRAMES_DIR, exist_ok=True)


# ---------------------------------------------------------------
# In-Memory Fast Cache for Store Materials (استجابة فورية 0.05ms)
# ---------------------------------------------------------------
import time

_MATERIALS_CACHE = {} # (page, per_page) -> (timestamp, PaginatedOut)
_CACHE_TTL_SECONDS = 30.0

def invalidate_materials_cache():
    """تفريغ الكاش فوراً عند إضافة أو تعديل أو حذف أي مادة لضمان التزامن الفوري"""
    _MATERIALS_CACHE.clear()

# ================================================================
# قائمة الملفات
# ================================================================

@router.get(
    "/",
    response_model = schemas.PaginatedOut,
    summary        = "قائمة الملفات المنشورة في المتجر",
)
def list_materials(
    page:    int = Query(1,  ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db:      Session = Depends(get_db),
):
    """
    إرجاع الملفات المنشورة مع pagination.
    متاح للجميع بدون تسجيل دخول مع كاش فائق السرعة في الذاكرة.
    """
    cache_key = (page, per_page)
    now = time.time()
    cached = _MATERIALS_CACHE.get(cache_key)
    if cached and (now - cached[0] < _CACHE_TTL_SECONDS):
        return cached[1]

    skip  = (page - 1) * per_page
    items, total = crud.get_published_materials(db, skip=skip, limit=per_page)

    result = schemas.PaginatedOut(
        items       = [schemas.MaterialOut.model_validate(m) for m in items],
        total       = total,
        page        = page,
        per_page    = per_page,
        total_pages = math.ceil(total / per_page) if total > 0 else 1,
    )
    _MATERIALS_CACHE[cache_key] = (now, result)
    return result


@router.get(
    "/admin/all",
    response_model = schemas.PaginatedOut,
    summary        = "كل الملفات (Admin فقط — بما فيها غير المنشورة)",
)
def list_all_materials(
    page:     int = Query(1,  ge=1),
    per_page: int = Query(50, ge=1, le=100),
    db:      Session = Depends(get_db),
    _admin:  User    = Depends(require_admin),
):
    skip  = (page - 1) * per_page
    items, total = crud.get_all_materials(db, skip=skip, limit=per_page)

    return schemas.PaginatedOut(
        items       = [schemas.MaterialOut.model_validate(m) for m in items],
        total       = total,
        page        = page,
        per_page    = per_page,
        total_pages = math.ceil(total / per_page) if total > 0 else 1,
    )


# ================================================================
# رفع ملف جديد (Admin فقط)
# ================================================================

@router.post(
    "/",
    response_model = schemas.MaterialOut,
    status_code    = status.HTTP_201_CREATED,
    summary        = "رفع ملف PDF جديد (Admin فقط)",
)
async def upload_material(
    # بيانات الملف كـ Form fields (مع ملف PDF)
    title:       str         = Form(...),
    tag:         Optional[str] = Form(None),
    description: str         = Form(None),
    price:       float       = Form(0.0),
    price_coins: float       = Form(...),
    pdf_file:    UploadFile  = File(..., description="ملف PDF فقط"),
    compression_enabled: bool = Form(True),
    cover_image: Optional[UploadFile] = File(None, description="صورة غلاف المذكرة"),
    page_frame:  Optional[UploadFile] = File(None, description="إطار الصفحة"),
    db:          Session     = Depends(get_db),
    admin:       User        = Depends(require_admin),
):
    """
    رفع ملف PDF جديد للمتجر.
    الملف بيتحفظ على السيرفر وبيتسجل في قاعدة البيانات.
    مش بيظهر في المتجر حتى يتعمله is_published = True.
    """
    # --- التحقق من نوع الملف ---
    if pdf_file.content_type != "application/pdf":
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail      = "الملف لازم يكون PDF فقط",
        )

    # --- التحقق من حجم الملف (الحد الأقصى: 50 ميجابايت) ---
    MAX_FILE_SIZE = 50 * 1024 * 1024
    pdf_file.file.seek(0, os.SEEK_END)
    file_size = pdf_file.file.tell()
    pdf_file.file.seek(0)
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail      = f"حجم الملف كبير جداً ({file_size // (1024*1024)}MB). الحد الأقصى هو 50MB.",
        )

    # --- حفظ الملف بـ اسم فريد ---
    file_id   = uuid.uuid4().hex
    file_name = f"{file_id}.pdf"
    file_path = os.path.join(UPLOAD_DIR, file_name)

    try:
        with open(file_path, "wb") as f:
            shutil.copyfileobj(pdf_file.file, f)
        logger.info(f"✓ [Upload] File saved to {file_path}")
    except Exception as e:
        logger.error(f"❌ [Upload Error] Failed to save file: {e}")
        raise HTTPException(status_code=500, detail="فشل في حفظ الملف على السيرفر")

    # --- قراءة عدد الصفحات والتحقق من الحد الأقصى ---
    total_pages = 0
    try:
        # استخدام timeout بسيط لو أمكن أو التأكد من عدم التعليق
        doc         = fitz.open(file_path)
        total_pages = len(doc)
        doc.close()
        
        MAX_PAGES = 600
        if total_pages > MAX_PAGES:
            if os.path.exists(file_path): os.remove(file_path)
            logger.warning(f"⚠️ [Upload] File too long: {total_pages} pages")
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail      = f"عدد صفحات الملف كبير جداً ({total_pages} صفحة). الحد الأقصى هو {MAX_PAGES} صفحة.",
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ [Upload Error] PDF processing failed: {e}")
        if os.path.exists(file_path): os.remove(file_path)
        raise HTTPException(status_code=400, detail="فشل في معالجة ملف الـ PDF - قد يكون الملف تالفاً أو محمياً بكلمة سر")

    # --- حفظ صورة الغلاف لو مرفوعة ---
    cover_image_path = None
    if cover_image:
        if not cover_image.content_type.startswith("image/"):
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail      = "ملف الغلاف يجب أن يكون صورة فقط",
            )
        img_id = uuid.uuid4().hex
        img_ext = os.path.splitext(cover_image.filename)[1] or ".png"
        img_name = f"{img_id}{img_ext}"
        img_path = os.path.join(COVERS_DIR, img_name)
        try:
            with open(img_path, "wb") as f:
                shutil.copyfileobj(cover_image.file, f)
            cover_image_path = f"/storage/covers/{img_name}"
            logger.info(f"✓ [Upload] Cover image saved to {img_path}")
        except Exception as e:
            logger.error(f"❌ [Upload Error] Failed to save cover image: {e}")
            raise HTTPException(status_code=500, detail="فشل في حفظ صورة الغلاف على السيرفر")
    else:
        # استخراج أول صفحة كغلاف
        try:
            doc = fitz.open(file_path)
            if len(doc) > 0:
                page = doc[0]
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                img_name = f"{uuid.uuid4().hex}.png"
                img_path = os.path.join(COVERS_DIR, img_name)
                pix.save(img_path)
                cover_image_path = f"/storage/covers/{img_name}"
                logger.info(f"✓ [Upload] Auto-extracted cover to {img_path}")
            doc.close()
        except Exception as e:
            logger.warning(f"⚠️ [Upload] Could not auto-extract cover from PDF: {e}")

    # --- حفظ إطار الصفحة لو مرفوع ---
    page_frame_path = None
    if page_frame:
        if not page_frame.content_type.startswith("image/"):
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail      = "ملف الإطار يجب أن يكون صورة فقط",
            )
        img_id = uuid.uuid4().hex
        img_ext = os.path.splitext(page_frame.filename)[1] or ".png"
        img_name = f"{img_id}{img_ext}"
        img_path = os.path.join(FRAMES_DIR, img_name)
        try:
            with open(img_path, "wb") as f:
                shutil.copyfileobj(page_frame.file, f)
            page_frame_path = f"/storage/frames/{img_name}"
            logger.info(f"✓ [Upload] Page frame saved to {img_path}")
        except Exception as e:
            logger.error(f"❌ [Upload Error] Failed to save page frame: {e}")
            raise HTTPException(status_code=500, detail="فشل في حفظ صورة الإطار على السيرفر")

    # --- إنشاء السجل في قاعدة البيانات ---
    try:
        data = schemas.MaterialCreate(
            title       = title,
            tag         = tag,
            description = description,
            price       = price,
            price_coins = price_coins,
            compression_enabled = compression_enabled,
            page_frame_path = page_frame_path,
        )
        material = crud.create_material(
            db          = db,
            data        = data,
            uploader_id = admin.id,
            pdf_path    = file_path,
            total_pages = total_pages,
            cover_image_path = cover_image_path,
        )
        invalidate_materials_cache()
        logger.info(f"✓ [Upload] Material created in DB: {material.id}")
        return schemas.MaterialOut.model_validate(material)
    except Exception as e:
        logger.error(f"❌ [Upload Error] DB creation failed: {e}")
        if os.path.exists(file_path): os.remove(file_path)
        raise HTTPException(status_code=500, detail="فشل في تسجيل بيانات الملف في قاعدة البيانات")


# ================================================================
# تفاصيل ملف معين
# ================================================================

@router.get(
    "/{material_id}",
    response_model = schemas.MaterialOut,
    summary        = "تفاصيل ملف معين",
)
def get_material(material_id: int, db: Session = Depends(get_db)):
    material = crud.get_material(db, material_id)
    if not material:
        raise HTTPException(status_code=404, detail="الملف غير موجود")
    if not material.is_published:
        raise HTTPException(status_code=404, detail="الملف غير متاح")
    return schemas.MaterialOut.model_validate(material)


# ================================================================
# جلب الملف الأصلي (Admin فقط — للمصمم)
# ================================================================

@router.get(
    "/{material_id}/original",
    summary        = "تحميل الملف الأصلي (Admin فقط — لاستخدام المصمم)",
)
def get_original_pdf(
    material_id: int,
    db:          Session = Depends(get_db),
    _admin:      User    = Depends(require_admin),
):
    """
    إرجاع ملف الـ PDF الأصلي بالكامل.
    يُستخدم فقط من قبل المسؤول في واجهة مصمم الأختام.
    """
    material = crud.get_material(db, material_id)
    if not material:
        raise HTTPException(status_code=404, detail="الملف غير موجود")

    if not os.path.exists(material.original_pdf_path):
        raise HTTPException(status_code=404, detail="الملف الأصلي غير موجود على السيرفر")

# ================================================================
# جلب الملف الأصلي كـ Base64 (Admin فقط — الحل النهائي لقوة التحميل)
# ================================================================

@router.get(
    "/{material_id}/designer-base64",
    summary        = "تحميل الملف كـ Base64 لضمان الاستقرار التام",
)
def get_designer_base64(
    material_id: int,
    db:          Session = Depends(get_db),
    admin:       User    = Depends(require_admin),
):
    """
    قراءة الملف وتحويله لنص Base64 وإرساله في JSON.
    أكثر استقراراً لـ Local development و PDF.js
    """
    material = crud.get_material(db, material_id)
    if not (material and os.path.exists(material.original_pdf_path)):
        raise HTTPException(status_code=404, detail="الملف غير موجود")

    with open(material.original_pdf_path, "rb") as f:
        encoded_string = base64.b64encode(f.read()).decode("utf-8")

    return {"pdf_64": encoded_string}


@router.post(
    "/{material_id}/designer-test-download",
    summary = "تحميل نسخة تجريبية للمعاينة (Admin فقط)",
)
async def designer_test_preview(
    material_id: int,
    data:        schemas.StampLayoutCreate, # نستخدم نفس الشيرما لاستلام التنسيق
    background_tasks: BackgroundTasks,
    db:          Session = Depends(get_db),
    _admin:      User    = Depends(require_admin),
):
    """
    توليد نسخة تجريبية من الملف بالأختام الحالية للمعاينة.
    يتم استخدام بيانات وهمية (اسم: تجربة مستخدم، هاتف: 01000000000).
    """
    material = crud.get_material(db, material_id)
    if not material or not os.path.exists(material.original_pdf_path):
        raise HTTPException(status_code=404, detail="الملف غير موجود")

    try:
        # تحويل الـ StampElements لـ Dicts
        layout_dicts = [el.model_dump() for el in data.stamp_elements]
        
        # تنفيذ الختم التجريبي
        test_pdf_path = await run_test_stamp(
            material_path = material.original_pdf_path,
            stamp_layout  = layout_dicts,
            material_tag  = material.tag
        )

        # حذف الملف من السيرفر بعد الإرسال
        background_tasks.add_task(lambda p: os.remove(p) if os.path.exists(p) else None, test_pdf_path)

        return FileResponse(
            path           = test_pdf_path,
            media_type     = "application/pdf",
            filename       = f"Test_Stamp_{material_id}.pdf",
            headers        = {"Content-Disposition": f"attachment; filename=Test_Stamp_{material_id}.pdf"}
        )

    except Exception as e:
        logger.error(f"[Designer Test Error]: {e}")
        raise HTTPException(status_code=500, detail=f"فشل توليد المعاينة: {str(e)}")


@router.post(
    "/{material_id}/designer-test-start",
    summary = "بدء توليد نسخة تجريبية في الخلفية (يرجع job_id فوراً)",
)
async def designer_test_start(
    material_id: int,
    data:        schemas.StampLayoutCreate,
    db:          Session = Depends(get_db),
    _admin:      User    = Depends(require_admin),
):
    """
    يبدأ عملية توليد النسخة التجريبية في الخلفية ويرجع job_id فوراً.
    المستخدم يعود للصفحة الرئيسية ويتابع الحالة عبر GET /api/jobs/{job_id}
    """
    material = crud.get_material(db, material_id)
    if not material or not os.path.exists(material.original_pdf_path):
        raise HTTPException(status_code=404, detail="الملف غير موجود")

    job_id    = uuid.uuid4().hex
    mat_title = material.title or f"ملف #{material_id}"
    jobs_store.create_job(job_id, user_id=_admin.id, label=f"نسخة تجريبية - {mat_title}")

    layout_dicts = [el.model_dump() for el in data.stamp_elements]
    mat_path     = material.original_pdf_path

    async def _run_in_bg():
        try:
            path = await run_test_stamp(
                material_path = mat_path,
                stamp_layout  = layout_dicts,
                material_tag  = material.tag
            )
            jobs_store.complete_job(job_id, path)
        except Exception as exc:
            jobs_store.fail_job(job_id, str(exc))
            logger.error(f"[Job {job_id}] فشل: {exc}")

    asyncio.create_task(_run_in_bg())

    return {"job_id": job_id, "label": mat_title}


@router.get(
    "/{material_id}/designer-file",
    summary        = "تحميل الملف الأصلي (Admin فقط) — دعم التوكن في الرابط لتجنب مشاكل الـ CORS",
)
def get_designer_file(
    material_id: int,
    db:          Session = Depends(get_db),
    admin:       User    = Depends(require_admin),
):
    """
    إرجاع ملف الـ PDF الأصلي بالكامل (للأدمن فقط).
    """
    material = crud.get_material(db, material_id)
    if not (material and os.path.exists(material.original_pdf_path)):
        raise HTTPException(status_code=404, detail="الملف غير موجود")

    return FileResponse(
        path           = material.original_pdf_path,
        media_type     = "application/pdf",
        headers        = {
            "Content-Disposition": "inline",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, OPTIONS",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Private-Network": "true"
        }
    )




# ================================================================
# تعديل وحذف (Admin فقط)
# ================================================================

@router.patch(
    "/{material_id}",
    response_model = schemas.MaterialOut,
    summary        = "تعديل بيانات ملف (Admin فقط)",
)
async def update_material(
    material_id: int,
    title:       Optional[str]       = Form(None),
    tag:         Optional[str]       = Form(None),
    description: Optional[str]       = Form(None),
    price:       Optional[float]     = Form(None),
    price_coins: Optional[float]     = Form(None),
    is_published: Optional[bool]     = Form(None),
    compression_enabled: Optional[bool] = Form(None),
    cover_image: Optional[UploadFile] = File(None),
    page_frame:  Optional[UploadFile] = File(None),
    db:          Session             = Depends(get_db),
    _admin:      User                = Depends(require_admin),
):
    material = crud.get_material(db, material_id)
    if not material:
        raise HTTPException(status_code=404, detail="الملف غير موجود")

    # Handle cover_image upload if provided
    cover_image_path = None
    if cover_image:
        if not cover_image.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="ملف الغلاف يجب أن يكون صورة فقط")
        img_id = uuid.uuid4().hex
        img_ext = os.path.splitext(cover_image.filename)[1] or ".png"
        img_name = f"{img_id}{img_ext}"
        img_path = os.path.join(COVERS_DIR, img_name)
        with open(img_path, "wb") as f:
            shutil.copyfileobj(cover_image.file, f)
        cover_image_path = f"/storage/covers/{img_name}"

    # Handle page_frame upload if provided
    page_frame_path = None
    if page_frame:
        if not page_frame.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="ملف الإطار يجب أن يكون صورة فقط")
        img_id = uuid.uuid4().hex
        img_ext = os.path.splitext(page_frame.filename)[1] or ".png"
        img_name = f"{img_id}{img_ext}"
        img_path = os.path.join(FRAMES_DIR, img_name)
        with open(img_path, "wb") as f:
            shutil.copyfileobj(page_frame.file, f)
        page_frame_path = f"/storage/frames/{img_name}"

    # Construct the update schema
    from decimal import Decimal
    update_dict = {}
    if title is not None: update_dict["title"] = title
    if tag is not None:
        update_dict["tag"] = None if tag in ("", "null", "None") else tag
    if description is not None: update_dict["description"] = description
    if price is not None: update_dict["price"] = Decimal(str(price))
    if price_coins is not None: update_dict["price_coins"] = Decimal(str(price_coins))
    logger.info(f"👉 [PATCH Update] Material {material_id}: is_published={is_published} (type: {type(is_published)})")
    if is_published is not None: update_dict["is_published"] = is_published
    if compression_enabled is not None: update_dict["compression_enabled"] = compression_enabled
    if cover_image_path is not None: update_dict["cover_image_path"] = cover_image_path
    if page_frame_path is not None: update_dict["page_frame_path"] = page_frame_path

    # Construct MaterialUpdate with only set fields
    update_data = schemas.MaterialUpdate.model_validate(update_dict)
    
    update_data.model_fields_set.clear()
    for k in update_dict.keys():
        update_data.model_fields_set.add(k)

    material = crud.update_material(db, material_id, update_data)
    invalidate_materials_cache()
    return schemas.MaterialOut.model_validate(material)


@router.delete(
    "/{material_id}",
    response_model = schemas.MessageOut,
    summary        = "حذف ملف (Admin فقط)",
)
def delete_material(
    material_id: int,
    db:          Session = Depends(get_db),
    _admin:      User    = Depends(require_admin),
):
    deleted = crud.delete_material(db, material_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="الملف غير موجود")
    invalidate_materials_cache()
    return schemas.MessageOut(message="تم حذف الملف بنجاح")


# ================================================================
# نظام المعاينة الآمنة
# ================================================================

@router.post(
    "/{material_id}/preview-token",
    response_model = schemas.PreviewTokenOut,
    summary        = "طلب توكن معاينة مؤقت",
)
def request_preview_token(
    material_id:  int,
    data:         schemas.PreviewTokenCreate,
    db:           Session = Depends(get_db),
    current_user: User    = Depends(get_current_user),
):
    """
    إنشاء توكن معاينة مؤقت صالح لـ 30 دقيقة.
    يُستخدم مع PDF.js في الـ Frontend لعرض الملف بأمان.
    """
    material = crud.get_material(db, material_id)
    if not material or not material.is_published:
        raise HTTPException(status_code=404, detail="الملف غير موجود")

    token = crud.create_preview_token(
        db          = db,
        material_id = material_id,
        user_id     = current_user.id,
    )
    return schemas.PreviewTokenOut.model_validate(token)


@router.get(
    "/preview/stream",
    summary = "معاينة الـ PDF كـ Binary Blob (آمنة من التحميل المباشر)",
)
def stream_preview(
    token: str     = Query(..., description="توكن المعاينة"),
    page:  int     = Query(1,   ge=1, description="رقم الصفحة"),
    db:    Session = Depends(get_db),
):
    """
    إرجاع صفحة واحدة من الـ PDF كـ binary stream.

    الأمان:
      - الـ token يتحقق منه قبل كل صفحة
      - page لازم تكون ضمن pages_allowed
      - الـ URL لا يكشف مسار الملف الأصلي على السيرفر
      - Content-Type: application/pdf + nosniff header يمنع التحميل المباشر
    """
    # --- التحقق من التوكن ---
    preview = crud.get_valid_preview_token(db, token)
    if not preview:
        raise HTTPException(status_code=401, detail="التوكن غير صالح أو منتهي")

    # --- التحقق من رقم الصفحة ---
    if page not in preview.allowed_pages:
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail      = f"غير مصرح بمعاينة الصفحة رقم {page}. الصفحات المتاحة: {preview.allowed_pages}",
        )

    # --- قراءة الصفحة المطلوبة وتحويلها لصورة عالية الجودة ---
    material = preview.material
    try:
        doc = fitz.open(material.original_pdf_path)
        page_obj = doc[page - 1]

        # High-DPI rendering: zoom 3x = ~216 DPI — واضحة وقابلة للقراءة
        zoom = 3.0
        pix = page_obj.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
        img_data = pix.tobytes("png")

        # إنشاء PDF يحتوي على الصورة عالية الجودة
        single_page_pdf = fitz.open()
        new_page = single_page_pdf.new_page(width=page_obj.rect.width, height=page_obj.rect.height)
        new_page.insert_image(new_page.rect, stream=img_data)

        pdf_bytes = single_page_pdf.tobytes(deflate=True, garbage=2)
        doc.close()
        single_page_pdf.close()

    except Exception as e:
        logger.error(f"[Preview Error] page {page}: {e}")
        raise HTTPException(status_code=500, detail="خطأ في قراءة الملف")

    # --- إرجاع الـ PDF كـ Base64 ---
    encoded_string = base64.b64encode(pdf_bytes).decode("utf-8")
    return {"pdf_64": encoded_string}


# ================================================================
# B2B Review & Rating Endpoints
# ================================================================

@router.post(
    "/{id}/reviews",
    response_model=schemas.ReviewOut,
    summary="كتابة أو تحديث مراجعة لمادة تعليمية",
)
def create_material_review(
    id: int,
    review_in: schemas.ReviewCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    كتابة مراجعة لمادة تعليمية.
    الشرط: يجب أن يكون المستخدم قد اشترى المادة بنجاح وحالتها 'completed'.
    """
    # 1. التحقق من وجود المادة
    material = db.query(models.Material).filter(models.Material.id == id).first()
    if not material:
        raise HTTPException(status_code=404, detail="المادة التعليمية غير موجودة")

    # 2. التحقق الأمني: هل قام المراجع بشراء المادة بنجاح؟
    purchase = db.query(Purchase).filter(
        Purchase.material_id == id,
        Purchase.buyer_id == current_user.id,
        Purchase.status == PurchaseStatus.COMPLETED
    ).first()
    if not purchase:
        raise HTTPException(
            status_code=403,
            detail="يجب شراء المادة أولاً لتتمكن من كتابة مراجعة وتقييم لها"
        )

    # 3. احتساب التقييم الإجمالي
    overall = round(
        (review_in.content_quality_rating +
         review_in.print_formatting_rating +
         review_in.stamp_appearance_rating) / 3.0,
        2
    )

    # 4. التحقق مما إذا كان هناك مراجعة سابقة للمستخدم لنفس المادة
    existing_review = db.query(Review).filter(
        Review.material_id == id,
        Review.user_id == current_user.id
    ).first()

    if existing_review:
        # تحديث المراجعة الحالية
        existing_review.reviewer_title = review_in.reviewer_title
        existing_review.content_quality_rating = review_in.content_quality_rating
        existing_review.print_formatting_rating = review_in.print_formatting_rating
        existing_review.stamp_appearance_rating = review_in.stamp_appearance_rating
        existing_review.overall_rating = overall
        existing_review.comment = review_in.comment
        existing_review.created_at = datetime.utcnow()
        db.commit()
        db.refresh(existing_review)
        review = existing_review
    else:
        # إنشاء مراجعة جديدة
        review = Review(
            material_id=id,
            user_id=current_user.id,
            reviewer_title=review_in.reviewer_title,
            content_quality_rating=review_in.content_quality_rating,
            print_formatting_rating=review_in.print_formatting_rating,
            stamp_appearance_rating=review_in.stamp_appearance_rating,
            overall_rating=overall,
            comment=review_in.comment
        )
        db.add(review)
        db.commit()
        db.refresh(review)

    return {
        "id": review.id,
        "material_id": review.material_id,
        "user_id": review.user_id,
        "reviewer_title": review.reviewer_title,
        "content_quality_rating": review.content_quality_rating,
        "print_formatting_rating": review.print_formatting_rating,
        "stamp_appearance_rating": review.stamp_appearance_rating,
        "overall_rating": float(review.overall_rating),
        "comment": review.comment,
        "created_at": review.created_at,
        "reviewer_name": current_user.full_name
    }


@router.get(
    "/{id}/reviews",
    response_model=schemas.MaterialReviewsOut,
    summary="جلب المراجعات ومتوسط التقييمات لمادة تعليمية",
)
def get_material_reviews(
    id: int,
    db: Session = Depends(get_db),
):
    """
    جلب كافة المراجعات لمادة معينة وحساب المتوسطات.
    """
    # 1. التحقق من وجود المادة
    material = db.query(models.Material).filter(models.Material.id == id).first()
    if not material:
        raise HTTPException(status_code=404, detail="المادة التعليمية غير موجودة")

    # 2. الاستعلام عن المراجعات ودمجها مع جدول المستخدمين للحصول على الاسم الكامل
    results = db.query(Review, User.full_name).join(
        User, Review.user_id == User.id
    ).filter(Review.material_id == id).order_by(Review.created_at.desc()).all()

    reviews_out = []
    total_count = len(results)

    avg_content = 0.0
    avg_print = 0.0
    avg_stamp = 0.0
    avg_overall = 0.0

    if total_count > 0:
        sum_content = 0
        sum_print = 0
        sum_stamp = 0
        sum_overall = 0.0

        for r, name in results:
            reviews_out.append({
                "id": r.id,
                "material_id": r.material_id,
                "user_id": r.user_id,
                "reviewer_title": r.reviewer_title,
                "content_quality_rating": r.content_quality_rating,
                "print_formatting_rating": r.print_formatting_rating,
                "stamp_appearance_rating": r.stamp_appearance_rating,
                "overall_rating": float(r.overall_rating),
                "comment": r.comment,
                "created_at": r.created_at,
                "reviewer_name": name
            })
            sum_content += r.content_quality_rating
            sum_print += r.print_formatting_rating
            sum_stamp += r.stamp_appearance_rating
            sum_overall += float(r.overall_rating)

        avg_content = round(sum_content / total_count, 1)
        avg_print = round(sum_print / total_count, 1)
        avg_stamp = round(sum_stamp / total_count, 1)
        avg_overall = round(sum_overall / total_count, 1)

    return {
        "reviews": reviews_out,
        "avg_content_quality": avg_content,
        "avg_print_formatting": avg_print,
        "avg_stamp_appearance": avg_stamp,
        "avg_overall": avg_overall,
        "total_count": total_count
    }


