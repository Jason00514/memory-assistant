from sqlalchemy.orm import Session
from app.models.memory_curve import MemoryCurve
from app.schemas.memory_curve import MemoryCurveCreate, MemoryCurveUpdate
from app.utils.id_generator import generate_mc_id


DEFAULT_CURVES = [
    {
        "curve_name": "标准单词曲线",
        "description": "适合英语单词记忆，强化初期复习频率",
        "intervals": [1, 4, 24, 48, 168, 360, 720],
        "overdue_multiplier": 15,
    },
    {
        "curve_name": "高频强化曲线",
        "description": "短周期强化记忆，适合考试冲刺",
        "intervals": [1, 2, 4, 8, 16, 36, 72],
        "overdue_multiplier": 10,
    },
    {
        "curve_name": "文章记忆曲线",
        "description": "适合长段落和文章记忆",
        "intervals": [24, 48, 96, 168, 288, 480, 720],
        "overdue_multiplier": 10,
    },
    {
        "curve_name": "日语单词曲线",
        "description": "适合日语词汇记忆",
        "intervals": [1, 4, 24, 72, 168, 336, 720],
        "overdue_multiplier": 12,
    },
]


def seed_default_curves(db: Session) -> None:
    if db.query(MemoryCurve).first():
        return
    for data in DEFAULT_CURVES:
        curve_id = generate_mc_id(db)
        curve = MemoryCurve(curve_id=curve_id, **data)
        db.add(curve)
        db.flush()  # make the new row visible to generate_mc_id on next iteration
    db.commit()


def get_default_curve(db: Session) -> MemoryCurve | None:
    return db.query(MemoryCurve).filter(MemoryCurve.data_flag == 0).first()


def get_curve(db: Session, curve_id: str) -> MemoryCurve | None:
    return db.query(MemoryCurve).filter(
        MemoryCurve.curve_id == curve_id,
        MemoryCurve.data_flag == 0,
    ).first()


def list_curves(db: Session) -> list[MemoryCurve]:
    return db.query(MemoryCurve).filter(MemoryCurve.data_flag == 0).all()


def create_curve(db: Session, data: MemoryCurveCreate) -> MemoryCurve:
    curve_id = generate_mc_id(db)
    curve = MemoryCurve(curve_id=curve_id, **data.model_dump())
    db.add(curve)
    db.commit()
    db.refresh(curve)
    return curve


def update_curve(db: Session, curve_id: str, data: MemoryCurveUpdate) -> MemoryCurve | None:
    curve = get_curve(db, curve_id)
    if not curve:
        return None
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(curve, field, value)
    db.commit()
    db.refresh(curve)
    return curve


def delete_curve(db: Session, curve_id: str) -> bool:
    curve = get_curve(db, curve_id)
    if not curve:
        return False
    curve.data_flag = 1
    db.commit()
    return True
