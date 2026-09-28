# ================================================================
# app/routers/presets.py — نقاط نهاية القوالب الجاهزة (Presets)
# ================================================================

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.auth import require_admin
from app.database import get_db
from app.models import User

router = APIRouter(prefix="/presets", tags=["قوالب الأختام"])

@router.get(
    "/",
    response_model = list[schemas.LayoutPresetOut],
    summary        = "قائمة القوالب الجاهزة",
)
def list_presets(
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    return crud.get_presets(db)


@router.post(
    "/",
    response_model = schemas.LayoutPresetOut,
    status_code    = status.HTTP_201_CREATED,
    summary        = "حفظ قالب جديد",
)
def save_preset(
    data: schemas.LayoutPresetCreate,
    db:   Session = Depends(get_db),
    admin: User   = Depends(require_admin),
):
    return crud.create_preset(db, data, admin.id)


@router.delete(
    "/{preset_id}",
    response_model = schemas.MessageOut,
    summary        = "حذف قالب",
)
def delete_preset(
    preset_id: int,
    db:        Session = Depends(get_db),
    _admin:    User    = Depends(require_admin),
):
    success = crud.delete_preset(db, preset_id)
    if not success:
        raise HTTPException(status_code=404, detail="القالب غير موجود")
    return schemas.MessageOut(message="تم حذف القالب بنجاح")
