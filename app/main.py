"""
FastAPI アプリケーションエントリーポイント。
起動時にテーブル作成・スキーママイグレーション・デフォルトデータのシードを行う。
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from app.core.database import engine, Base, SessionLocal
from app.models import RawContent, ProcessedContent, MemoryCurve  # noqa: F401 — テーブル登録のため必要
from app.routers import import_excel, review, curves, cards, dashboard
from app.crud.memory_curve import seed_default_curves

app = FastAPI(
    title="记忆助手 API",
    description="基于7级遗忘曲线的记忆管理系统",
    version="1.1.0",
)

# フロントエンド（Vite dev server）からのアクセスを許可
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全ルーターを登録
app.include_router(import_excel.router)
app.include_router(review.router)
app.include_router(curves.router)
app.include_router(cards.router)
app.include_router(dashboard.router)


def _run_migrations() -> None:
    """
    シンプルなスキーママイグレーション。
    新しいカラムが存在しない場合のみ ALTER TABLE を実行する。
    SQLite は ALTER TABLE でカラム追加のみサポート（削除・変更は不可）。
    """
    with engine.connect() as conn:
        # tags カラムを追加（v1.1 で追加）
        try:
            conn.execute(text("ALTER TABLE processed_contents ADD COLUMN tags JSON"))
            conn.commit()
        except Exception:
            pass  # 既に存在する場合は無視


@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(bind=engine)  # テーブルが存在しない場合のみ作成
    _run_migrations()                       # 差分カラムを追加
    db = SessionLocal()
    try:
        seed_default_curves(db)             # デフォルトカーブをシード
    finally:
        db.close()


@app.get("/")
def root():
    return {"message": "记忆助手 API is running", "version": "1.1.0"}
