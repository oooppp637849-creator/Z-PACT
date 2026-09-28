# ================================================================
# app/routers/stats.py — إحصائيات المنصة (Dashboard Stats)
# ================================================================

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from typing import Dict, Any, List

from app.database import get_db
from app.models import User, Purchase, Material, CoinTransaction, TransactionType, WalletTransaction
from app.auth import get_current_user

router = APIRouter(prefix="/stats", tags=["الإحصائيات"])

@router.get("/dashboard")
def get_dashboard_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """جلب إحصائيات لوحة التحكم للمسؤول"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="ليس لديك صلاحية")

    # 1. إحصائيات عامة
    total_users = db.query(User).count()
    total_materials = db.query(Material).count()
    total_purchases = db.query(Purchase).count()
    
    # إجمالي الأرباح (من الشحنات المكتملة)
    total_revenue = db.query(func.sum(WalletTransaction.amount)).filter(WalletTransaction.status == "completed").scalar() or 0
    
    # 2. إحصائيات آخر 30 يوم (Revenue)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    daily_revenue = (
        db.query(
            func.date(WalletTransaction.transaction_date).label("date"),
            func.sum(WalletTransaction.amount).label("total")
        )
        .filter(WalletTransaction.status == "completed")
        .filter(WalletTransaction.transaction_date >= thirty_days_ago)
        .group_by(func.date(WalletTransaction.transaction_date))
        .all()
    )
    
    # 3. إحصائيات نمو المستخدمين
    daily_users = (
        db.query(
            func.date(User.created_at).label("date"),
            func.count(User.id).label("count")
        )
        .filter(User.created_at >= thirty_days_ago)
        .group_by(func.date(User.created_at))
        .all()
    )

    # 4. أفضل 5 مواد مبيعاً
    top_materials = (
        db.query(
            Material.title,
            func.count(Purchase.id).label("sales_count")
        )
        .join(Purchase, Purchase.material_id == Material.id)
        .group_by(Material.id)
        .order_by(desc("sales_count"))
        .limit(5)
        .all()
    )

    return {
        "summary": {
            "total_users": total_users,
            "total_materials": total_materials,
            "total_purchases": total_purchases,
            "total_revenue": float(total_revenue)
        },
        "charts": {
            "revenue": [{"date": str(r.date), "amount": float(r.total)} for r in daily_revenue],
            "users": [{"date": str(u.date), "count": u.count} for u in daily_users]
        },
        "top_selling": [{"title": m.title, "sales": m.sales_count} for m in top_materials]
    }
