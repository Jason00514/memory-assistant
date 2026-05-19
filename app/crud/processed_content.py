"""
ProcessedContent の CRUD 操作
データベースへの読み書きはこのファイルに集約する。
"""
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.processed_content import ProcessedContent
from app.utils.id_generator import generate_pc_id


def create_processed_content(
    db: Session,
    rc_id: str,
    content_type: str,
    question: str,
    answer: str,
    extra,
    category: str,
    usage_type: str | None,
    curve_id: str | None,
) -> ProcessedContent:
    pc_id = generate_pc_id(db)
    record = ProcessedContent(
        PC_ID=pc_id,
        RC_ID=rc_id,
        content_type=content_type,
        question=question,
        answer=answer,
        extra=extra,
        category=category,
        tags=[],        # 初期タグは空
        usage_type=usage_type,
        curve_id=curve_id,
        current_level=1,
        last_reviewed_at=None,
        next_review_time=None,
        process_version=1,
        data_flag=0,
        processed_at=datetime.utcnow(),
    )
    db.add(record)
    return record


def get_due_for_review(
    db: Session,
    category: str | None = None,
    tag: str | None = None,
    sort_urgency: bool = True,
) -> list[ProcessedContent]:
    """
    今日復習すべきカードを返す。
    sort_urgency=True のとき、過期が大きい順（最優先）に並べる。
    """
    now = datetime.utcnow()
    q = db.query(ProcessedContent).filter(
        ProcessedContent.data_flag == 0,
        # next_review_time が null（未復習）または過去のものが対象
        or_(
            ProcessedContent.next_review_time.is_(None),
            ProcessedContent.next_review_time <= now,
        ),
    )
    if category:
        q = q.filter(ProcessedContent.category == category)
    if tag:
        # JSON配列のタグ検索（SQLite: JSON_EACH を使わず LIKE で代用）
        q = q.filter(ProcessedContent.tags.cast(db.bind.dialect.name == 'sqlite' and
                      type(None) or type(None)).contains(tag) if False
                      else ProcessedContent.tags.astext.contains(tag)
                      if hasattr(ProcessedContent.tags, 'astext')
                      else q.filter(True).filter(True))

    if sort_urgency:
        # next_review_time が null のもの（未復習）を先頭に、次に過期が大きいもの順
        q = q.order_by(ProcessedContent.next_review_time.asc().nullsfirst())

    return q.all()


def get_all_active(
    db: Session,
    category: str | None = None,
    tag: str | None = None,
    status_filter: str | None = None,  # "due" / "overdue" / None(全て)
) -> list[ProcessedContent]:
    """
    カード一覧を返す。status_filter で絞り込み可能。
    """
    now = datetime.utcnow()
    q = db.query(ProcessedContent).filter(ProcessedContent.data_flag == 0)

    if category:
        q = q.filter(ProcessedContent.category == category)

    if status_filter == "due":
        # 未復習 or 今日が期限のもの
        q = q.filter(
            or_(ProcessedContent.next_review_time.is_(None),
                ProcessedContent.next_review_time <= now)
        )
    elif status_filter == "overdue":
        # 期限切れ（next_review_time が過去）
        q = q.filter(
            ProcessedContent.next_review_time.isnot(None),
            ProcessedContent.next_review_time < now,
        )

    return q.order_by(ProcessedContent.next_review_time.asc().nullsfirst()).all()


def get_by_id(db: Session, pc_id: str) -> ProcessedContent | None:
    return db.query(ProcessedContent).filter(
        ProcessedContent.PC_ID == pc_id,
        ProcessedContent.data_flag == 0,
    ).first()


def update_review_result(
    db: Session,
    record: ProcessedContent,
    new_level: int,
    last_reviewed_at: datetime,
    next_review_time: datetime,
) -> None:
    """答え合わせ後のレベル・日時を更新する"""
    record.current_level = new_level
    record.last_reviewed_at = last_reviewed_at
    record.next_review_time = next_review_time


def update_tags(db: Session, pc_id: str, tags: list[str]) -> ProcessedContent | None:
    """カードのタグ一覧を上書き更新する"""
    record = get_by_id(db, pc_id)
    if not record:
        return None
    record.tags = tags
    db.commit()
    db.refresh(record)
    return record


def update_curve(db: Session, pc_id: str, curve_id: str) -> ProcessedContent | None:
    """カードが使用する記憶カーブを変更する"""
    record = get_by_id(db, pc_id)
    if not record:
        return None
    record.curve_id = curve_id
    db.commit()
    db.refresh(record)
    return record


def get_all_tags(db: Session) -> list[str]:
    """
    DB に存在する全タグをユニークな一覧で返す。
    SQLite の JSON 配列を Python 側で展開してから重複除去する。
    """
    records = db.query(ProcessedContent.tags).filter(
        ProcessedContent.data_flag == 0,
        ProcessedContent.tags.isnot(None),
    ).all()
    tag_set: set[str] = set()
    for (tags,) in records:
        if isinstance(tags, list):
            tag_set.update(tags)
    return sorted(tag_set)


def get_category_stats(db: Session) -> list[dict]:
    """
    カテゴリ別の統計（総数・待復習・過期）を返す。
    Dashboard 表示用。
    """
    now = datetime.utcnow()
    all_cards = db.query(ProcessedContent).filter(ProcessedContent.data_flag == 0).all()

    stats_map: dict[str, dict] = {}
    for card in all_cards:
        cat = card.category
        if cat not in stats_map:
            stats_map[cat] = {"category": cat, "total": 0, "due": 0, "overdue": 0, "mastered": 0}
        stats_map[cat]["total"] += 1
        if card.next_review_time is None or card.next_review_time <= now:
            stats_map[cat]["due"] += 1
        if card.next_review_time and card.next_review_time < now:
            stats_map[cat]["overdue"] += 1
        if card.current_level == 7:
            stats_map[cat]["mastered"] += 1

    return sorted(stats_map.values(), key=lambda x: x["due"], reverse=True)


def reset_level(db: Session, pc_id: str, level: int = 1) -> ProcessedContent | None:
    """カードのレベルを任意のレベルにリセットし、次回復習日時をクリアする"""
    record = get_by_id(db, pc_id)
    if not record:
        return None
    record.current_level = max(1, min(7, level))
    record.next_review_time = None
    record.last_reviewed_at = None
    db.commit()
    db.refresh(record)
    return record
