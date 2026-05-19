"""
インポートルーター：Excel / テキストファイルの取り込みと解析
"""
import io
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.crud import raw_content as crud_raw
from app.crud import processed_content as crud_pc
from app.crud import memory_curve as crud_curve
from app.schemas.raw_content import ImportResult, RawContentOut
from app.schemas.processed_content import ProcessRequest, ProcessResult, ProcessedContentOut
from app.services.excel_parser import parse_excel_stream
from app.services.text_parser import parse_text_content
from app.services.content_parser import parse_raw_content

router = APIRouter(prefix="/import", tags=["import"])


def _save_records(db: Session, records_data: list[dict]) -> tuple[list, int]:
    """
    raw record リストを DB に保存し、(成功リスト, 失敗数) を返す。
    各レコード保存後に flush() することで ID 重複を防ぐ。
    """
    created = []
    failed = 0
    for data in records_data:
        try:
            record = crud_raw.create_raw_content(
                db,
                category=data["category"],
                content_type=data["content_type"],
                raw_text=data["raw_text"],
            )
            db.flush()   # 次のレコードが同じ ID を生成しないよう都度 flush
            created.append(record)
        except Exception:
            db.rollback()
            failed += 1
    db.commit()
    return created, failed


@router.post("/excel", response_model=ImportResult)
async def import_excel(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Excel ファイル（.xlsx/.xls）を読み込み RawContent として保存する"""
    if not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(status_code=400, detail="Only .xlsx / .xls files are accepted")

    contents = await file.read()
    records_data = parse_excel_stream(io.BytesIO(contents))
    created, failed = _save_records(db, records_data)

    return ImportResult(
        total_imported=len(created),
        failed=failed,
        items=[RawContentOut.model_validate(r) for r in created],
    )


@router.post("/text", response_model=ImportResult)
async def import_text(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """テキストファイル（.txt）を読み込み RawContent として保存する"""
    if not file.filename.endswith(".txt"):
        raise HTTPException(status_code=400, detail="Only .txt files are accepted")

    raw_bytes = await file.read()
    text = raw_bytes.decode("utf-8", errors="replace")
    records_data = parse_text_content(text)
    created, failed = _save_records(db, records_data)

    return ImportResult(
        total_imported=len(created),
        failed=failed,
        items=[RawContentOut.model_validate(r) for r in created],
    )


@router.post("/process", response_model=ProcessResult)
def process_raw_contents(
    request: ProcessRequest,
    db: Session = Depends(get_db),
):
    """
    未処理の RawContent を解析して ProcessedContent（復習カード）を生成する。
    rc_ids を指定した場合はそのレコードのみ処理。未指定は全未処理対象。
    """
    if request.rc_ids:
        raw_records = crud_raw.get_by_ids(db, request.rc_ids)
    else:
        raw_records = crud_raw.get_unprocessed(db)

    # カーブ未指定の場合はデフォルトカーブを使用
    curve_id = request.curve_id
    if not curve_id:
        default_curve = crud_curve.get_default_curve(db)
        curve_id = default_curve.curve_id if default_curve else None

    processed = []
    failed = 0

    for raw in raw_records:
        try:
            crud_raw.set_process_status(db, raw, "processing")
            db.flush()

            parsed = parse_raw_content(raw.content_type, raw.raw_text)
            pc = crud_pc.create_processed_content(
                db,
                rc_id=raw.RC_ID,
                content_type=raw.content_type,
                question=parsed["question"],
                answer=parsed["answer"],
                extra=parsed.get("extra"),
                category=raw.category,
                usage_type=parsed.get("usage_type"),
                curve_id=curve_id,
            )
            crud_raw.set_process_status(db, raw, "processed")
            db.flush()   # PC_ID 重複防止
            processed.append(pc)
        except Exception:
            failed += 1
            crud_raw.set_process_status(db, raw, "failed")

    db.commit()
    return ProcessResult(
        total_processed=len(processed),
        failed=failed,
        items=[ProcessedContentOut.model_validate(p) for p in processed],
    )


@router.get("/raw", response_model=list[RawContentOut])
def list_raw(
    category: str | None = Query(None),
    db: Session = Depends(get_db),
):
    """インポート済みの生データ一覧を返す"""
    return crud_raw.list_raw_contents(db, category=category)
