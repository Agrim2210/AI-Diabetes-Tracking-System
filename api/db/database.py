from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from api.core.config import settings

# ── Engine ────────────────────────────────────────────────────────────────────
# pool_pre_ping=True: test connection health before using it from the pool

engine = create_engine(
    settings.get_database_url(),    
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=(settings.APP_ENV == "development"),
)

# ── Session Factory ───────────────────────────────────────────────────────────
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# ── Base Class for ORM Models ─────────────────────────────────────────────────
Base = declarative_base()


def create_tables():
    """Create all tables defined in models.py — call once on app startup."""
    from api.db import models  # noqa: F401  — import so Base sees the models
    Base.metadata.create_all(bind=engine)