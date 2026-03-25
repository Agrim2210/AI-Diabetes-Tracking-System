from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from api.core.config import settings

# ── Engine ────────────────────────────────────────────────────────────────────
# pool_pre_ping=True: test connection health before using it from the pool
# pool_recycle=3600: recycle connections every hour to avoid MySQL's 8hr timeout

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=(settings.APP_ENV == "development"),  # log SQL queries in dev only
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