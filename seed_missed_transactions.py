# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

"""
seed_missed_transactions.py
============================
سكريبت يُشغَّل مرة واحدة فقط لإضافة التحويلات
التي وصلت للسيرفر من الـ SMS لكن لم تُحفظ في قاعدة البيانات.

كيفية التشغيل:
  python seed_missed_transactions.py

الضمانات:
  ✅ لو التحويل موجود بالفعل في الداتا بيز → يتخطاه
  ✅ حتى لو التحويل اتستخدم في شراء سابق → ما يتضافش مرة تانية
  ✅ يشتغل مرة واحدة بس ولا يعمل حاجة لو مفيش جديد
"""

import sys
import os
from datetime import datetime

# ── إضافة مسار المشروع لـ Python Path ─────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config import settings
from app.database import SessionLocal, create_tables
from app.models import WalletTransaction

# ================================================================
# ✏️ التحويلات الفائتة (مستخرجة من الـ logs يدوياً)
# أضف هنا أي تحويل ظهر في الـ logs لكن لم يتم حفظه
# ================================================================
MISSED_TRANSACTIONS = [
    {
        "sender_phone": "شريف محمد فرج",       # CIB لا يُرسل رقم هاتف، بنستخدم الاسم
        "amount": 80.0,
        "source": "InstaPay",
        "note": "تحويل CIB لحظي - رقم مرجعي 357018762882 - 2026-05-13 16:00",
        # وقت التحويل الفعلي من الـ log
        "transaction_date": datetime(2026, 5, 13, 13, 0, 30),  # UTC من الـ log
    },
    # ─── أضف تحويلات فائتة إضافية هنا بنفس الشكل ───
    # {
    #     "sender_phone": "01xxxxxxxxx",
    #     "amount": 150.0,
    #     "source": "VodafoneCash",
    #     "note": "وصف التحويل",
    #     "transaction_date": datetime(2026, 5, 13, 14, 30, 0),
    # },
]


def seed():
    # إنشاء الجداول لو مش موجودة (ضروري للـ local dev — على Railway هي موجودة بالفعل)
    create_tables()
    db = SessionLocal()
    added = 0
    skipped = 0

    print("=" * 55)
    print("[START] بدء اضافة التحويلات الفائتة...")
    print("=" * 55)

    for tx in MISSED_TRANSACTIONS:
        note = tx.get("note", "")
        tx_date = tx.get("transaction_date")

        # ── فحص التكرار: هل موجود بنفس الرقم + المبلغ؟ ──
        # نبحث بفارق زمني ±24 ساعة من وقت التحويل الأصلي
        from datetime import timedelta
        window_start = (tx_date - timedelta(hours=24)) if tx_date else datetime(2020, 1, 1)
        window_end   = (tx_date + timedelta(hours=24)) if tx_date else datetime.utcnow()

        existing = db.query(WalletTransaction).filter(
            WalletTransaction.sender_phone == str(tx["sender_phone"]),
            WalletTransaction.amount       == float(tx["amount"]),
            WalletTransaction.transaction_date >= window_start,
            WalletTransaction.transaction_date <= window_end,
        ).first()

        if existing:
            status_label = "مكتمل" if existing.status == "completed" else "معلق"
            print(f"  [SKIP] موجود بالفعل (ID={existing.id}, الحالة: {status_label}): "
                  f"{tx['amount']} من '{tx['sender_phone']}' - تخطي")
            skipped += 1
            continue

        # ── إضافة التحويل ──
        new_tx = WalletTransaction(
            sender_phone     = str(tx["sender_phone"]),
            amount           = float(tx["amount"]),
            source           = tx.get("source", "InstaPay"),
            status           = "pending",  # يبقى معلق لحين استخدامه في شراء
            transaction_date = tx_date or datetime.utcnow(),
        )
        db.add(new_tx)
        db.flush()  # نحصل على الـ ID قبل الـ commit

        print(f"  [OK] تمت الاضافة (ID={new_tx.id}): "
              f"{tx['amount']} من '{tx['sender_phone']}'"
              f"{' - ' + note if note else ''}")
        added += 1

    db.commit()
    db.close()

    print("=" * 55)
    print(f"[RESULT] تمت الاضافة: {added} | موجودين مسبقاً: {skipped}")
    print("=" * 55)

    if added == 0 and skipped > 0:
        print("[DONE] لا يوجد جديد - الداتا بيز محدثة بالفعل.")
    elif added > 0:
        print("[SUCCESS] تمت الاضافة. يمكنك مطابقتها من لوحة الادارة.")


if __name__ == "__main__":
    seed()
