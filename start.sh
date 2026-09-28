#!/bin/bash

# ================================================================
# WebPDF Elite - Production Entrypoint Script
# ================================================================

# ================================================================
# إعداد مسارات التخزين الدائمة على Railway Volume
# Railway Volume مربوط على /.data مباشرةً داخل الـ Container
# DATABASE_URL يشير بالفعل لـ .data/webpdf_elite.db = /.data/webpdf_elite.db
# ================================================================

echo "📂 Setting up persistent directories on Railway Volume (/.data)..."

# إنشاء مجلدات الملفات (storage) داخل الـ Volume نفسه
mkdir -p /.data/storage/originals
mkdir -p /.data/storage/stamped
mkdir -p /.data/storage/previews
mkdir -p /.data/storage/avatars

# ربط مجلد storage بالمجلد الدائم على الـ Volume
# هذا يضمن أن الملفات المرفوعة (PDF, صور) تُحفظ بشكل دائم
if [ ! -L "/app/storage" ]; then
    rm -rf /app/storage 2>/dev/null || true
    ln -sf /.data/storage /app/storage
    echo "✅ Linked /app/storage → /.data/storage"
fi

echo "🚀 Starting WebPDF Elite Production Server..."

# تشغيل خادم Gunicorn مع عمال Uvicorn لضمان أقصى أداء وثبات
exec gunicorn main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --timeout 600 \
    --access-log-file - \
    --error-log-file -

