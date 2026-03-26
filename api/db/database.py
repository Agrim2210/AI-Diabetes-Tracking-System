from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from api.core.config import settings

# ── Engine ────────────────────────────────────────────────────────────────────
# pool_pre_ping=True: test connection health before using it from the pool


# Build URL — works both locally and on Render
db_url = settings.DATABASE_URL or (
    f"postgresql+psycopg2://{settings.DB_USER}:{settings.DB_PASSWORD}"
    f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
)

# Render gives postgres:// — SQLAlchemy needs postgresql://
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

engine = create_engine(
    db_url,
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