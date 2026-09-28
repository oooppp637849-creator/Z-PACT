# ================================================================
# app/stamper.py — محرك الختم (PDF Stamping Engine) v3.0
#
# ده قلب المشروع كله.
# بياخد الـ PDF الأصلي + بيانات المشتري + تنسيق الأختام
# ويرجع PDF مختوم، محمي بكلمة سر، فيه علامات مخفية.
#
# المحرك الجديد (v3): يستخدم PyMuPDF فقط لإضافة الأختام والعلامات
# المائية مباشرة على الـ PDF الأصلي بدون أي تحويل لصور (Vector-Preserving).
# ================================================================

import asyncio
import math
import os
import random
import uuid
from pathlib import Path
from typing import Optional

import fitz  # PyMuPDF
fitz.TOOLS.mupdf_display_errors(False)

from sqlalchemy.orm import Session
from app.formatting import format_instructor_name, format_contact_phone, clean_phone_number

from app import crud
from app.database import SessionLocal
from app.models import MarkType, PurchaseStatus
from app.config import settings
from app.logger import logger

# مسار مجلد تخزين الملفات المختومة
OUTPUT_DIR = os.path.join(settings.STORAGE_DIR, "stamped")
PREVIEW_DIR = os.path.join(settings.STORAGE_DIR, "previews")
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(PREVIEW_DIR, exist_ok=True)

# سيمفور لتحديد عدد العمليات المتزامنة
STAMP_SEMAPHORE = asyncio.Semaphore(2)

# مسار خط Cairo لاستخدامه في الأختام العربية
_CAIRO_FONT_PATH = os.path.abspath(os.path.join(settings.BASE_DIR, "frontend", "assets", "Cairo-Bold.ttf"))
if not os.path.exists(_CAIRO_FONT_PATH):
    _CAIRO_FONT_PATH = None  # سيستخدم الخط الافتراضي

_CAIRO_FONT = None

def _get_font() -> fitz.Font:
    """إرجاع كائن خط Cairo مخزن مسبقاً لتسريع المعالجة وجودة الرسم"""
    global _CAIRO_FONT
    if _CAIRO_FONT is not None:
        return _CAIRO_FONT
    if _CAIRO_FONT_PATH and os.path.exists(_CAIRO_FONT_PATH):
        try:
            _CAIRO_FONT = fitz.Font(fontfile=_CAIRO_FONT_PATH)
            return _CAIRO_FONT
        except Exception as e:
            logger.warning(f"Could not load Cairo font: {e}")
    return fitz.Font("helv")


# ================================================================
# دالة المدخل الرئيسية — بتُستدعى من الـ Background Task
# ================================================================

async def stamp_pdf(
    purchase_id:    int,
    material_path:  str,
    stamp_layout:   list[dict],
    buyer_name:     str,
    buyer_phone:    str,
    watermark_text: Optional[str] = None,
    doc_name_stamp: Optional[str] = None,
    compress:       bool = True,
    is_encrypted:   bool = False,
    material_tag:   Optional[str] = None,
    watermark_type: Optional[str] = "text",
    watermark_logo_path: Optional[str] = None,
) -> None:
    """
    الدالة الرئيسية لختم الـ PDF.
    بتُنفَّذ في الـ background بعد تسجيل الشراء مباشرة.
    """
    from app.routers.chat import manager
    db = SessionLocal()

    async with STAMP_SEMAPHORE:
        try:
            logger.info(f"🚀 [Stamper] Starting process for Purchase {purchase_id}")
            crud.update_purchase_status(db, purchase_id, PurchaseStatus.PROCESSING)

            purchase = crud.get_purchase(db, purchase_id)
            page_frame_path = None
            if purchase and purchase.material and purchase.material.page_frame_path:
                cleaned_frame = purchase.material.page_frame_path.lstrip('/')
                page_frame_path = os.path.abspath(cleaned_frame)
                if not os.path.exists(page_frame_path):
                    page_frame_path = os.path.abspath(os.path.join(settings.STORAGE_DIR, "..", cleaned_frame))
                if not os.path.exists(page_frame_path):
                    page_frame_path = None

            buyer_phone_2 = purchase.buyer_phone_stamp_2 if purchase else None

            # --- الخطوة 1: ختم بـ PyMuPDF (Vector-Preserving) ---
            try:
                stamped_path = await asyncio.wait_for(
                    asyncio.to_thread(
                        _stamp_native,
                        purchase_id,
                        material_path,
                        stamp_layout,
                        buyer_name,
                        buyer_phone,
                        watermark_text,
                        doc_name_stamp,
                        material_tag,
                        page_frame_path,
                        watermark_type,
                        watermark_logo_path,
                        buyer_phone_2,
                    ),
                    timeout=600.0  # 10 دقائق
                )
            except asyncio.TimeoutError:
                raise Exception("تخطى محرك الختم المهلة الزمنية (10 دقائق). الملف كبير جداً أو السيرفر مشغول.")

            logger.info(f"✓ [Stamper] Native stamping finished for {purchase_id}")

            # --- التحقق الأمني ---
            if not os.path.exists(stamped_path) or os.path.getsize(stamped_path) < 5000:
                raise Exception(f"فشل توليد الملف: الملف الناتج غير صالح (size={os.path.getsize(stamped_path) if os.path.exists(stamped_path) else 0})")

            check_doc = fitz.open(stamped_path)
            check_pages = len(check_doc)
            check_doc.close()
            original_doc = fitz.open(material_path)
            original_pages = len(original_doc)
            original_doc.close()
            logger.info(f"[Stamper] Verification for {purchase_id}: stamped_pages={check_pages}, original_pages={original_pages}")

            if check_pages != original_pages:
                raise Exception(f"خرق أمني: الملف الناتج به {check_pages} صفحة بدلاً من {original_pages}.")

            # --- الخطوة 2: إضافة علامات مخفية ---
            logger.info(f"⏳ [Stamper] Adding hidden marks for {purchase_id}...")
            final_path = _add_marks_and_finalize(
                db           = db,
                input_path   = stamped_path,
                purchase_id  = purchase_id,
                buyer_name   = buyer_name,
                buyer_phone  = buyer_phone,
                compress     = compress,
                is_encrypted = is_encrypted,
            )

            if not os.path.exists(final_path) or os.path.getsize(final_path) < 5000:
                raise Exception("فشل في المرحلة النهائية من معالجة الملف")

            # --- الخطوة 3: تحديث قاعدة البيانات ---
            purchase = crud.update_purchase_status(
                db          = db,
                purchase_id = purchase_id,
                status      = PurchaseStatus.COMPLETED,
                output_path = final_path,
            )
            logger.info(f"✅ [Stamper] Purchase {purchase_id} COMPLETED ({os.path.getsize(final_path)//1024}KB)")

            if purchase and purchase.buyer_id:
                await manager.send_personal_message(purchase.buyer_id, {
                    "action": "job_update",
                    "purchase_id": purchase_id,
                    "status": "completed",
                    "title": purchase.material.title if purchase.material else "ملف جاهز"
                })

        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            logger.error(f"❌ [Stamper Error] Purchase {purchase_id}: {e}\n--- Traceback ---\n{tb}")
            try:
                purchase = crud.update_purchase_status(db, purchase_id, PurchaseStatus.FAILED)
                if purchase and purchase.buyer_id:
                    await manager.send_personal_message(purchase.buyer_id, {
                        "action": "job_update",
                        "purchase_id": purchase_id,
                        "status": "failed",
                        "error": str(e)
                    })
            except:
                pass

        finally:
            db.close()


async def run_test_stamp(
    material_path: str,
    stamp_layout:  list[dict],
    material_tag:  Optional[str] = None,
    page_frame_path: Optional[str] = None,
) -> str:
    """
    ختم تجريبي سريع للمعاينة.
    بدون تشفير وبدون علامات مخفية وبدون تسجيل في الداتا بيز.
    """
    import shutil

    def _do_test():
        tmp_dir = PREVIEW_DIR
        os.makedirs(tmp_dir, exist_ok=True)
        fake_id = "test_" + uuid.uuid4().hex[:8]

        has_logo_elements = any(el.get("type") == "logo_watermark" for el in stamp_layout)
        watermark_type = "logo" if has_logo_elements else "text"

        raw_pdf = _stamp_native(
            fake_id,
            material_path,
            stamp_layout,
            "تجربة مستخدم",
            "01000000000",
            "نسخة معاينة",
            "اسم المذكرة التجريبي",
            material_tag=material_tag,
            page_frame_path=page_frame_path,
            watermark_type=watermark_type,
            watermark_logo_path=None,
        )
        final_dest = f"{tmp_dir}/test_{fake_id}.pdf"
        shutil.copy(raw_pdf, final_dest)
        return final_dest

    return await asyncio.to_thread(_do_test)


# ================================================================
# المحرك الأساسي: ختم مباشر بـ PyMuPDF (Vector-Preserving)
# ================================================================

def _stamp_native(
    purchase_id,
    material_path:  str,
    stamp_layout:   list[dict],
    buyer_name:     str,
    buyer_phone:    str,
    watermark_text: Optional[str] = None,
    doc_name_stamp: Optional[str] = None,
    material_tag:   Optional[str] = None,
    page_frame_path: Optional[str] = None,
    watermark_type: Optional[str] = "text",
    watermark_logo_path: Optional[str] = None,
    buyer_phone_2:  Optional[str] = None,
) -> str:
    """
    يفتح الـ PDF الأصلي ويضيف الأختام والعلامات المائية مباشرة
    على الطبقة الفوقية (overlay) باستخدام PyMuPDF فقط.
    بدون أي تحويل لصور — يحافظ على الجودة المتجهة 100%.
    """
    doc = fitz.open(material_path)
    total_pages = len(doc)

    # --- تنسيق البيانات ---
    formatted_name  = format_instructor_name(buyer_name)
    formatted_phone = format_contact_phone(buyer_phone)
    smart_doc_name  = doc_name_stamp.strip() if doc_name_stamp else ""
    smart_wm_text   = watermark_text.strip() if watermark_text else ""
    if watermark_type == "logo":
        smart_wm_text = ""

    # --- تجهيز اللوجو ---
    logo_elements = []
    logo_path = None
    if watermark_type == "logo":
        logo_elements = [el for el in stamp_layout if el.get("type") == "logo_watermark"]
        if watermark_logo_path:
            cleaned_logo = watermark_logo_path.lstrip('/')
            abs_logo_path = os.path.abspath(cleaned_logo)
            if os.path.exists(abs_logo_path):
                logo_path = abs_logo_path
            else:
                fallback = os.path.abspath(os.path.join(settings.STORAGE_DIR, "..", cleaned_logo))
                if os.path.exists(fallback):
                    logo_path = fallback
        if not logo_path:
            logo_path = os.path.abspath("frontend/assets/logo.png")

    # --- تسجيل خط Cairo إن وجد ---
    font_name = "helv"  # الخط الافتراضي
    if _CAIRO_FONT_PATH:
        try:
            font_name = "cairo"
            # سنسجل الخط في كل صفحة عند الحاجة
        except Exception:
            font_name = "helv"

    # --- معالجة كل صفحة ---
    for i in range(total_pages):
        page = doc[i]
        page_num = i + 1
        pw = page.rect.width
        ph = page.rect.height

        # === Layer 0: إطار الصفحة (خلفية) ===
        if page_frame_path and os.path.exists(page_frame_path):
            try:
                page.insert_image(page.rect, filename=page_frame_path, keep_proportion=False, overlay=True)
            except Exception as e:
                logger.error(f"❌ [Frame Error] Page {page_num}: {e}")

        # === Layer 1: اللوجو المائي (PyMuPDF مباشر) ===
        for el in logo_elements:
            _draw_logo_on_page(page, el, page_num, logo_path)

        # === Layer 2: الأختام النصية والعلامة المائية ===
        page_stamps = _get_stamps_for_page(stamp_layout, page_num, total_pages)

        for stamp in page_stamps:
            stamp_type = stamp.get("type", "")

            # تحديد النص المعروض
            is_single_page = int(stamp.get("page", 0)) > 0
            is_literal = (total_pages == 1) or is_single_page

            if stamp_type == "name":
                display_text = formatted_name
            elif stamp_type == "phone":
                if page_num == 1:
                    # في صفحة الغلاف (الصفحة الأولى)، يظهر الرقم فقط بدون "ت /"
                    display_text = clean_phone_number(buyer_phone)
                elif buyer_phone_2:
                    display_text = format_contact_phone(buyer_phone) if (page_num % 2 == 1) else format_contact_phone(buyer_phone_2)
                else:
                    display_text = formatted_phone
            elif stamp_type == "doc_name":
                display_text = smart_doc_name if is_literal else _get_smart_text(smart_doc_name, "سلسلة", material_tag)
            elif stamp_type == "watermark":
                if watermark_type == "logo":
                    display_text = ""
                elif is_literal:
                    display_text = smart_wm_text
                else:
                    display_text = _get_smart_text(smart_wm_text, "", material_tag)
            else:
                display_text = stamp.get("custom_text", "")

            if not display_text:
                continue

            # --- رسم الختم ---
            _draw_text_stamp_on_page(page, stamp, display_text, pw, ph, font_name)

        # === Layer 3: DCT Watermark (Frequency Domain) ===
        try:
            p_id = int(purchase_id)
            # DCT watermark يتم تطبيقه على الصور المضمنة في الصفحة
            # (يتطلب rasterization لصفحة واحدة فقط — مؤقتاً)
            # تم تعطيله مؤقتاً لتجنب rasterization
        except ValueError:
            pass

    # --- حفظ الملف ---
    output_path = f"{OUTPUT_DIR}/{purchase_id}_stamped.pdf"
    doc.save(output_path, garbage=4, deflate=True)
    doc.close()
    logger.info(f"[Stamper] Saved stamped PDF: {os.path.getsize(output_path)//1024}KB, pages={total_pages}")
    return output_path


# ================================================================
# دوال مساعدة للرسم المباشر على الـ PDF
# ================================================================

def _get_stamps_for_page(stamp_layout: list[dict], page_num: int, total_pages: int) -> list[dict]:
    """تجميع الأختام المخصصة لصفحة معينة."""
    result = []
    for el in stamp_layout:
        if el.get("type") == "logo_watermark":
            continue  # اللوجو يُعالج بشكل منفصل

        try:
            target_page = int(el.get("page", 0))
        except (TypeError, ValueError):
            target_page = 0
        try:
            exclusions = [int(x) for x in el.get("excluded_pages", [])]
        except (TypeError, ValueError):
            exclusions = []

        if target_page == 0:
            if page_num not in exclusions:
                result.append(el)
        elif target_page == page_num:
            result.append(el)
    return result


def _draw_logo_on_page(page, el: dict, page_num: int, logo_path: str):
    """رسم اللوجو المائي على صفحة PyMuPDF."""
    try:
        target_page = int(el.get("page", 0))
    except (TypeError, ValueError):
        target_page = 0
    try:
        exclusions = [int(x) for x in el.get("excluded_pages", [])]
    except (TypeError, ValueError):
        exclusions = []

    if target_page == 0 and page_num in exclusions:
        return
    if target_page > 0 and target_page != page_num:
        return

    if not logo_path or not os.path.exists(logo_path):
        return

    scale = el.get("font_size", 10.0) * 10.0
    if scale <= 0:
        scale = 150.0

    w = page.rect.width
    h = page.rect.height
    cx = (el.get("x_pct", 50.0) / 100.0) * w
    cy = (el.get("y_pct", 50.0) / 100.0) * h
    rect = fitz.Rect(cx - scale/2, cy - scale/2, cx + scale/2, cy + scale/2)

    op = float(el.get("opacity", 0.15))
    # يتم رسم شعار العلامة المائية فوق المحتوى (under_content = False) لضمان ظهوره
    under_content = False

    try:
        from PIL import Image
        import io

        pil_img = Image.open(logo_path).convert("RGBA")
        r, g, b, a = pil_img.split()
        a = a.point(lambda x: int(x * op))
        pil_img = Image.merge("RGBA", (r, g, b, a))

        buf = io.BytesIO()
        pil_img.save(buf, format="PNG")
        buf.seek(0)
        page.insert_image(rect, stream=buf.read(), keep_proportion=True, overlay=not under_content)
    except Exception:
        page.insert_image(rect, filename=logo_path, keep_proportion=True, overlay=not under_content)


def _draw_text_stamp_on_page(page, stamp: dict, text: str, pw: float, ph: float, font_name: str):
    """رسم ختم نصي على صفحة PyMuPDF بدقة عالية."""
    # تشكيل وإعادة توجيه النصوص العربية لتعرض بشكل صحيح (متصلة ومن اليمين إلى اليسار مع دعم الروابط الحرفية)
    if text:
        has_arabic = any('\u0600' <= char <= '\u06FF' or '\u0750' <= char <= '\u077F' or '\u08A0' <= char <= '\u08FF' or '\uFB50' <= char <= '\uFDFF' or '\uFE70' <= char <= '\uFEFF' for char in text)
        if has_arabic:
            try:
                import arabic_reshaper
                from bidi.algorithm import get_display
                reshaper = arabic_reshaper.ArabicReshaper(
                    configuration={
                        'delete_harakat': False,
                        'support_ligatures': True,
                        'support_transparent_glyphs': True
                    }
                )
                reshaped = reshaper.reshape(text)
                text = get_display(reshaped)
            except Exception as e:
                logger.error(f"Error reshaping Arabic text: {e}")

    x_pct   = float(stamp.get("x_pct", 50))
    y_pct   = float(stamp.get("y_pct", 50))
    fsize   = float(stamp.get("font_size", 14))
    rotation = float(stamp.get("rotation", 0))
    opacity  = float(stamp.get("opacity", 1.0))
    color_hex = stamp.get("color", "#000000")
    pattern   = stamp.get("pattern", "single")
    stamp_type = stamp.get("type", "")

    # تحويل اللون من hex إلى RGB tuple (0-1)
    color = _hex_to_rgb(color_hex)

    # تحديد Z-index:
    overlay_val = True

    # --- نمط Tiled (علامة مائية مكررة) ---
    if pattern == "tiled" and stamp_type == "watermark":
        _draw_tiled_watermark(page, text, fsize, color, opacity, overlay_val)
        return

    # --- نمط Diagonal (علامة مائية قطرية) ---
    if pattern == "diagonal" and stamp_type == "watermark":
        fsize = min(fsize, 100)
        _draw_diagonal_watermark(page, text, fsize, color, opacity, overlay_val)
        return

    # --- نمط Standard (ختم عادي) ---
    if stamp_type == "watermark":
        fsize = min(fsize, 120)

    cx = (x_pct / 100.0) * pw
    cy = (y_pct / 100.0) * ph

    # إنشاء TextWriter لدعم النص العربي
    tw = fitz.TextWriter(page.rect)
    font = _get_font()

    # حساب عرض النص لتوسيطه
    text_width = font.text_length(text, fontsize=fsize)
    text_height = fsize

    # نقطة البداية (مع التوسيط)
    start_x = cx - text_width / 2
    start_y = cy + text_height / 3  # تعديل عمودي لتوسيط بصري

    try:
        tw.append((start_x, start_y), text, font=font, fontsize=fsize)
    except Exception as e:
        logger.warning(f"tw.append error: {e}. Falling back to insert_text with font.")
        try:
            page.insert_text(
                point    = fitz.Point(start_x, start_y),
                text     = text,
                fontfile = _CAIRO_FONT_PATH if _CAIRO_FONT_PATH else None,
                fontsize = fsize,
                color    = color,
                overlay  = overlay_val,
            )
        except Exception:
            page.insert_text(
                point    = fitz.Point(start_x, start_y),
                text     = text,
                fontsize = fsize,
                color    = color,
                overlay  = overlay_val,
            )
        return

    # تطبيق الدوران إن وجد
    if abs(rotation) > 0.5:
        morph = (fitz.Point(cx, cy), fitz.Matrix(1, 0, 0, 1, 0, 0).prerotate(rotation))
        tw.write_text(page, color=color, opacity=opacity, overlay=overlay_val, morph=morph)
    else:
        tw.write_text(page, color=color, opacity=opacity, overlay=overlay_val)


def _draw_tiled_watermark(page, text: str, fsize: float, color: tuple, opacity: float, overlay: bool):
    """رسم علامة مائية مكررة (tiled) على الصفحة."""
    pw = page.rect.width
    ph = page.rect.height

    font = _get_font()

    tile_fsize = min(fsize, 60)
    text_w = font.text_length(text, fontsize=tile_fsize)
    gap_x = text_w + 80
    gap_y = tile_fsize * 3

    angle = -30  # زاوية الدوران

    tw = fitz.TextWriter(page.rect)
    y = -ph * 0.3
    while y < ph * 1.3:
        x = -pw * 0.3
        while x < pw * 1.3:
            try:
                tw.append((x, y), text, font=font, fontsize=tile_fsize)
            except Exception:
                pass
            x += gap_x
        y += gap_y

    morph = (fitz.Point(pw/2, ph/2), fitz.Matrix(1,0,0,1,0,0).prerotate(angle))
    tw.write_text(page, color=color, opacity=opacity, overlay=overlay, morph=morph)


def _draw_diagonal_watermark(page, text: str, fsize: float, color: tuple, opacity: float, overlay: bool):
    """رسم علامة مائية قطرية واحدة في منتصف الصفحة."""
    pw = page.rect.width
    ph = page.rect.height

    font = _get_font()

    text_w = font.text_length(text, fontsize=fsize)
    cx = pw / 2
    cy = ph / 2
    start_x = cx - text_w / 2
    start_y = cy + fsize / 3

    tw = fitz.TextWriter(page.rect)
    try:
        tw.append((start_x, start_y), text, font=font, fontsize=fsize)
    except Exception:
        page.insert_text(fitz.Point(start_x, start_y), text, fontfile=_CAIRO_FONT_PATH if _CAIRO_FONT_PATH else None, fontsize=fsize, color=color, overlay=overlay)
        return

    morph = (fitz.Point(cx, cy), fitz.Matrix(1,0,0,1,0,0).prerotate(-45))
    tw.write_text(page, color=color, opacity=opacity, overlay=overlay, morph=morph)


def _hex_to_rgb(hex_color: str) -> tuple:
    """تحويل لون hex إلى RGB tuple (0.0 - 1.0)."""
    hex_color = hex_color.lstrip("#")
    if len(hex_color) == 3:
        hex_color = "".join(c*2 for c in hex_color)
    try:
        r = int(hex_color[0:2], 16) / 255.0
        g = int(hex_color[2:4], 16) / 255.0
        b = int(hex_color[4:6], 16) / 255.0
        return (r, g, b)
    except (ValueError, IndexError):
        return (0.0, 0.0, 0.0)


# ================================================================
# استخراج اسم الغلاف الذكي
# ================================================================

import re as _re

def _extract_cover_name(doc_name: str) -> str:
    if not doc_name: return ""
    name = doc_name.strip()
    pattern = _re.compile(r'^سلسل(?:ة|ه)\s+(.+?)\s+في\s+', _re.UNICODE)
    m = pattern.match(name)
    if m:
        return m.group(1).strip()
    if len(name.split()) == 1 and any('\u0600' <= c <= '\u06FF' for c in name):
        return name
    return name

def _get_smart_text(original_text: str, subject_prefix: str = "سلسلة", subject_tag: str = "") -> str:
    """
    تحويل ذكي للنص:
    - لو النص أكثر من كلمة واحدة (مثل: 'لا للنشر' أو عبارات مخصصة):
      يُعرض النص كما كتبه المستخدم تماماً بدون إضافة 'سلسلة' أو 'في {subject_tag}'.
    - لو النص كلمة واحدة فقط (مثل: 'تفوق' أو 'التفوق'):
      يتم تحويله تلقائياً لـ: [سلسلة] [الكلمة] في [المادة].
    """
    if not original_text:
        return ""
    text = original_text.strip()
    words = text.split()

    # إذا كان النص يتكون من أكثر من كلمة واحدة: يُترك النص تماماً كما هو
    if len(words) > 1:
        return text

    # إذا كان النص كلمة واحدة فقط:
    clean_text = _re.sub(r'^(سلسل(?:ة|ه))\s+', '', text, flags=_re.UNICODE).strip()
    if subject_tag:
        suffix_pat = _re.compile(rf'\s+في\s+{_re.escape(subject_tag)}$', _re.UNICODE)
        clean_text = suffix_pat.sub('', clean_text).strip()

    prefix = f"{subject_prefix} " if subject_prefix else ""
    suffix = f" في {subject_tag}" if subject_tag else ""
    return f"{prefix}{clean_text}{suffix}".strip()


# ================================================================
# تنسيق بيانات المدرس
# ================================================================

def _format_teacher_name(name: str) -> str:
    return format_instructor_name(name)

def _format_phone_number(phone: str) -> str:
    return format_contact_phone(phone)


# ================================================================
# الخطوة النهائية: إضافة علامات مخفية (Steganography)
# بدون أي rasterization — يعمل مباشرة على الـ PDF المتجهي
# ================================================================

def _add_marks_and_finalize(
    db:          Session,
    input_path:  str,
    purchase_id: int,
    buyer_name:  str,
    buyer_phone: str,
    compress:    bool = True,
    is_encrypted: bool = False,
) -> str:
    """
    إضافة العلامات المخفية للتتبع مباشرة على الـ PDF المتجهي.
    بدون rasterization — يحافظ على الجودة الأصلية 100%.
    """
    output_path = f"{OUTPUT_DIR}/{purchase_id}_final.pdf"
    doc = fitz.open(input_path)

    from app import crud
    purchase = crud.get_purchase(db, purchase_id)

    for page_num in range(len(doc)):
        page = doc[page_num]
        random_suffix = uuid.uuid4().hex[:6].upper()
        short_mark = f"E-{purchase_id}-{random_suffix}"

        width  = page.rect.width
        height = page.rect.height

        # --- Steganography: نص مخفي في الزوايا ---
        corners = [
            (width * random.uniform(0.01, 0.15), height * random.uniform(0.01, 0.15)),
            (width * random.uniform(0.85, 0.99), height * random.uniform(0.01, 0.15)),
            (width * random.uniform(0.01, 0.15), height * random.uniform(0.85, 0.99)),
            (width * random.uniform(0.85, 0.99), height * random.uniform(0.85, 0.99)),
        ]

        for (x, y) in corners:
            page.insert_text(
                point    = fitz.Point(x, y),
                text     = short_mark,
                fontsize = 1,
                color    = (1, 1, 1),  # أبيض تماماً
            )
            crud.record_hidden_mark(
                db          = db,
                purchase_id = purchase_id,
                page_number = page_num + 1,
                x_pct       = (x / width) * 100,
                y_pct       = (y / height) * 100,
                mark_code   = short_mark,
                mark_type   = MarkType.INVISIBLE_TEXT,
            )

        # --- Micro-dots ---
        dot_rng = random.Random(purchase_id * 1000 + (page_num + 1))
        for _ in range(dot_rng.randint(4, 5)):
            x_dot = (dot_rng.uniform(5.0, 95.0) / 100.0) * width
            y_dot = (dot_rng.uniform(5.0, 95.0) / 100.0) * height
            page.draw_circle(
                center = fitz.Point(x_dot, y_dot),
                radius = 1,
                color  = (0.1, 0.1, 0.1),
                fill   = (0.1, 0.1, 0.1),
                stroke_opacity = 0.05,
                fill_opacity = 0.05,
            )

    # --- إعداد خيارات الحفظ ---
    save_options = {
        "garbage": 4 if compress else 0,
        "deflate": compress,
    }

    if is_encrypted:
        save_options["encryption"] = fitz.PDF_ENCRYPT_AES_256
        save_options["user_pw"] = buyer_phone
        save_options["owner_pw"] = buyer_phone

    doc.save(output_path, **save_options)
    doc.close()
    logger.info(f"[Stamper] Final PDF saved: {os.path.getsize(output_path)//1024}KB")
    return output_path
