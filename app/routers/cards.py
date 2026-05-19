"""
カード管理ルーター：タグ更新・カーブ変更・タグ一覧取得
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.crud import processed_content as crud
from app.schemas.processed_content import ProcessedContentOut, UpdateTagsRequest, UpdateCurveRequest

router = APIRouter(prefix="/cards", tags=["cards"])


@router.get("/tags", response_model=list[str])
def list_tags(db: Session = Depends(get_db)):
    """DB に存在する全タグをユニーク一覧で返す"""
    return crud.get_all_tags(db)


@router.put("/{pc_id}/tags", response_model=ProcessedContentOut)
def update_tags(pc_id: str, body: UpdateTagsRequest, db: Session = Depends(get_db)):
    """指定カードのタグを上書き更新する"""
    record = crud.update_tags(db, pc_id, body.tags)
    if not record:
        raise HTTPException(status_code=404, detail="Card not found")
    return record


@router.put("/{pc_id}/curve", response_model=ProcessedContentOut)
def update_curve(pc_id: str, body: UpdateCurveRequest, db: Session = Depends(get_db)):
    """指定カードの記憶カーブを変更する"""
    record = crud.update_curve(db, pc_id, body.curve_id)
    if not record:
        raise HTTPException(status_code=404, detail="Card not found")
    return record
