"""
Run this script once to create all tables and seed default memory curves.
Usage: python migrations/init_db.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import engine, Base, SessionLocal
from app.models import RawContent, ProcessedContent, MemoryCurve  # noqa
from app.crud.memory_curve import seed_default_curves

Base.metadata.create_all(bind=engine)
print("Tables created.")

db = SessionLocal()
try:
    seed_default_curves(db)
    print("Default memory curves seeded.")
finally:
    db.close()
