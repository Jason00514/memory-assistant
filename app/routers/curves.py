from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.crud import memory_curve as crud
from app.schemas.memory_curve import MemoryCurveCreate, MemoryCurveUpdate, MemoryCurveOut

router = APIRouter(prefix="/curves", tags=["memory-curves"])


@router.get("/", response_model=list[MemoryCurveOut])
def list_curves(db: Session = Depends(get_db)):
    return crud.list_curves(db)


@router.post("/", response_model=MemoryCurveOut)
def create_curve(data: MemoryCurveCreate, db: Session = Depends(get_db)):
    return crud.create_curve(db, data)


@router.get("/{curve_id}", response_model=MemoryCurveOut)
def get_curve(curve_id: str, db: Session = Depends(get_db)):
    curve = crud.get_curve(db, curve_id)
    if not curve:
        raise HTTPException(status_code=404, detail="Curve not found")
    return curve


@router.put("/{curve_id}", response_model=MemoryCurveOut)
def update_curve(curve_id: str, data: MemoryCurveUpdate, db: Session = Depends(get_db)):
    curve = crud.update_curve(db, curve_id, data)
    if not curve:
        raise HTTPException(status_code=404, detail="Curve not found")
    return curve


@router.delete("/{curve_id}")
def delete_curve(curve_id: str, db: Session = Depends(get_db)):
    if not crud.delete_curve(db, curve_id):
        raise HTTPException(status_code=404, detail="Curve not found")
    return {"message": "Deleted"}
