# ================================================================
# WebPDF Elite - Production Dockerfile
# ================================================================

# استخدام صورة بايثون خفيفة ومستقرة (Bookworm)
FROM python:3.10-slim-bookworm

# ضبط متغيرات البيئة لمنع تأخير المخرجات (Logs) وإنشاء ملفات .pyc
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# تحديد مجلد العمل داخل الحاوية
WORKDIR /app

# تثبيت الاعتماديات الأساسية للنظام (Linux dependencies)
# تم إضافة المكتبات اللازمة لـ Playwright و Chromium بشكل يدوي لتجنب مشاكل الخطوط في Debian
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    curl \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpango-1.0-0 \
    libcairo2 \
    && rm -rf /var/lib/apt/lists/*

# نسخ ملف المتطلبات أولاً للاستفادة من الـ caching في Docker
COPY requirements.txt .

# تثبيت مكتبات بايثون
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# تثبيت متصفح Chromium والاعتماديات الخاصة به بشكل رسمي
RUN playwright install chromium && playwright install-deps chromium

# نسخ كافة ملفات المشروع إلى الحاوية
COPY . .

# إنشاء مجلدات التخزين والتأكد من وجودها
RUN mkdir -p storage/originals storage/stamped storage/previews

# جعل سكريبت التشغيل قابلاً للتنفيذ
RUN chmod +x start.sh

# فتح المنفذ 8000
EXPOSE 8000

# تشغيل التطبيق عبر سكريبت البداية
CMD ["./start.sh"]
