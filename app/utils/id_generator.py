from sqlalchemy.orm import Session


def generate_rc_id(db: Session) -> str:
    from app.models.raw_content import RawContent
    last = db.query(RawContent).order_by(RawContent.RC_ID.desc()).first()
    if last:
        num = int(last.RC_ID[3:]) + 1
    else:
        num = 1
    return f"RC_{num:07d}"


def generate_pc_id(db: Session) -> str:
    from app.models.processed_content import ProcessedContent
    last = db.query(ProcessedContent).order_by(ProcessedContent.PC_ID.desc()).first()
    if last:
        num = int(last.PC_ID[3:]) + 1
    else:
        num = 1
    return f"PC_{num:07d}"


def generate_mc_id(db: Session) -> str:
    from app.models.memory_curve import MemoryCurve
    last = db.query(MemoryCurve).order_by(MemoryCurve.curve_id.desc()).first()
    if last:
        num = int(last.curve_id[3:]) + 1
    else:
        num = 1
    return f"MC_{num:06d}"
