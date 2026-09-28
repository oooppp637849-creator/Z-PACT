# WebPDF Elite — منصة بيع وحماية ملفات PDF 🔐

## هيكل المشروع الكامل

```
webpdf_elite/
│
├── main.py                     ← نقطة بداية FastAPI
├── requirements.txt            ← المكتبات المطلوبة
│
├── app/
│   ├── models.py               ← جداول قاعدة البيانات (SQLAlchemy)
│   ├── schemas.py              ← تحقق البيانات (Pydantic)
│   ├── crud.py                 ← عمليات قاعدة البيانات
│   ├── database.py             ← إعداد الاتصال بـ SQLite
│   ├── auth.py                 ← نظام JWT + Dependencies
│   ├── stamper.py              ← محرك الختم (Playwright + PyMuPDF)
│   │
│   └── routers/
│       ├── auth.py             ← /api/auth/* (تسجيل + دخول)
│       ├── materials.py        ← /api/materials/* (الملفات)
│       └── purchases.py        ← /api/purchases/* (المشتريات)
│
└── storage/
    ├── originals/              ← الملفات الأصلية المرفوعة
    ├── stamped/                ← الملفات المختومة النهائية
    └── tmp/                    ← ملفات مؤقتة أثناء الختم
```

---

## تشغيل المشروع

```bash
# 1. تثبيت المكتبات
pip install -r requirements.txt

# 2. تثبيت Chromium لـ Playwright
playwright install chromium

# 3. تشغيل السيرفر
uvicorn main:app --reload --port 8000

# API Docs متاحة على:
# http://localhost:8000/api/docs
```

---

## الـ API Endpoints

| Method | Endpoint | الوصف | الصلاحية |
|--------|----------|-------|----------|
| POST | /api/auth/register | تسجيل مستخدم جديد | عام |
| POST | /api/auth/login | تسجيل الدخول | عام |
| GET | /api/auth/me | بياناتي | مسجل |
| GET | /api/materials/ | قائمة الملفات | عام |
| POST | /api/materials/ | رفع ملف جديد | Admin |
| PATCH | /api/materials/{id} | تعديل ملف | Admin |
| DELETE | /api/materials/{id} | حذف ملف | Admin |
| POST | /api/materials/{id}/preview-token | طلب معاينة | مسجل |
| GET | /api/materials/preview/stream | معاينة آمنة | بتوكن |
| POST | /api/purchases/ | شراء ملف | مسجل |
| GET | /api/purchases/ | مشترياتي | مسجل |
| POST | /api/purchases/{id}/download-token | طلب تحميل | مسجل |
| GET | /api/purchases/download | تحميل الملف المختوم | بتوكن |

---

## دورة حياة الختم

```
Admin يرفع PDF  →  يصمم تنسيق الأختام (Drag & Drop)
     ↓
Customer يشتري  →  يُدخل اسمه ورقمه  →  يختار التنسيق
     ↓
Backend (Background Task):
  1. تحويل كل صفحة PDF → PNG
  2. بناء HTML بالأختام فوق الصور
  3. Playwright يطبع الـ HTML كـ PDF
  4. PyMuPDF يشفر الـ PDF بكلمة سر = رقم الهاتف
  5. إضافة نص مخفي (1pt أبيض) في كل زاوية
  6. تسجيل العلامات في قاعدة البيانات
     ↓
Customer يحصل على رابط تحميل مؤقت (10 دقائق)
```

---

## طبقات الحماية من التسريب

| الطبقة | الوصف |
|--------|-------|
| ختم مرئي | الاسم + الهاتف مطبوع على الصفحات |
| تشفير PDF | كلمة سر = رقم الهاتف (AES-256) |
| علامة مخفية | نص أبيض 1pt في كل زاوية كل صفحة |
| معاينة آمنة | Binary blob فقط — لا رابط مباشر للملف |
| توكن تحميل | صالح 10 دقائق، استخدام واحد فقط |

---

## المهام القادمة

- [ ] **المهمة 5**: واجهة الـ Admin (رفع + تصميم الأختام بـ Drag & Drop)
- [ ] **المهمة 6**: واجهة العميل (المتجر + المعاينة + الشراء)
- [ ] **المهمة 7**: محرك PDF.js مع Binary Loading
- [ ] **المهمة 8**: نظام الأختام بـ Drag & Drop (Canvas / CSS)
