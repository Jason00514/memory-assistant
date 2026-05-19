from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.crud import raw_content as crud_raw
from app.crud import processed_content as crud_pc
from app.crud import memory_curve as crud_curve
from app.schemas.raw_content import ImportResult, RawContentOut
from app.schemas.processed_content import ProcessRequest, ProcessResult, ProcessedContentOut
from app.services.excel_parser import parse_excel_stream
from app.services.content_parser import parse_raw_content

router = APIRouter(prefix="/import", tags=["import"])


@router.post("/excel", response_model=ImportResult)
async def import_excel(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(status_code=400, detail="Only .xlsx / .xls files are accepted")

    contents = await file.read()
    import io
    records_data = parse_excel_stream(io.BytesIO(contents))

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
            db.flush()  # make new row visible to ID generator for next iteration
            created.append(record)
        except Exception:
            db.rollback()
            failed += 1

    db.commit()
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
    if request.rc_ids:
        raw_records = crud_raw.get_by_ids(db, request.rc_ids)
    else:
        raw_records = crud_raw.get_unprocessed(db)

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
            db.flush()  # make new row visible to ID generator
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
    return crud_raw.list_raw_contents(db, category=category)
