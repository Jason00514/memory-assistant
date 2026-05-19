from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import engine, Base
from app.models import RawContent, ProcessedContent, MemoryCurve  # noqa: F401 — ensure models are registered
from app.routers import import_excel, review, curves
from app.crud.memory_curve import seed_default_curves
from app.core.database import SessionLocal

app = FastAPI(
    title="记忆助手 API",
    description="基于7级遗忘曲线的记忆管理系统",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(import_excel.router)
app.include_router(review.router)
app.include_router(curves.router)


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_default_curves(db)
    finally:
        db.close()


@app.get("/")
def root():
    return {"message": "记忆助手 API is running"}
