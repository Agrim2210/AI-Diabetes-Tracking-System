from datetime import datetime
from sqlalchemy import (
    Column, Integer, Float, String, Boolean,
    DateTime, ForeignKey, Text, Enum
)
from sqlalchemy.orm import relationship
from api.db.database import Base
import enum


# ── Enums ─────────────────────────────────────────────────────────────────────

class RiskLevel(str, enum.Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


# ── Users ─────────────────────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id          = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username    = Column(String(50), unique=True, nullable=False, index=True)
    email       = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name   = Column(String(100), nullable=True)
    is_active   = Column(Boolean, default=True, nullable=False)
    created_at  = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at  = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # ── Relationships ─────────────────────────────────
    predictions     = relationship("Prediction", back_populates="user", cascade="all, delete-orphan")
    health_analyses = relationship("HealthAnalysis", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User id={self.id} username={self.username}>"


# ── Predictions ───────────────────────────────────────────────────────────────

class Prediction(Base):
    __tablename__ = "predictions"

    id           = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id      = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # ── Patient input fields (matches your PatientData schema) ────────────────
    pregnancies  = Column(Integer, nullable=False)
    glucose      = Column(Float, nullable=False)
    blood_pressure   = Column(Float, nullable=False)
    skin_thickness   = Column(Float, nullable=False)
    insulin      = Column(Float, nullable=False)
    bmi          = Column(Float, nullable=False)
    diabetes_pedigree_function = Column(Float, nullable=False)
    age          = Column(Integer, nullable=False)

    # ── Model output ──────────────────────────────────────────────────────────
    result       = Column(Integer, nullable=False)          # 0 = no diabetes, 1 = diabetes
    probability  = Column(Float, nullable=False)            # model confidence (0.0 – 1.0)
    risk_level   = Column(Enum(RiskLevel), nullable=False)  # Low / Medium / High
    advice       = Column(Text, nullable=True)              # health advice text

    predicted_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # ── Relationships ─────────────────────────────────
    user = relationship("User", back_populates="predictions")

    def __repr__(self):
        return f"<Prediction id={self.id} user_id={self.user_id} result={self.result}>"


# ── Health Analyses ───────────────────────────────────────────────────────────

class HealthAnalysis(Base):
    __tablename__ = "health_analyses"

    id              = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id         = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    total_predictions   = Column(Integer, nullable=False, default=0)
    diabetic_count      = Column(Integer, nullable=False, default=0)
    non_diabetic_count  = Column(Integer, nullable=False, default=0)

    avg_glucose     = Column(Float, nullable=True)
    avg_bmi         = Column(Float, nullable=True)
    avg_blood_pressure  = Column(Float, nullable=True)

    risk_progression    = Column(String(20), nullable=True)   # "Improving" / "Worsening" / "Stable"
    trend_summary       = Column(Text, nullable=True)         # human-readable summary
    health_insights     = Column(Text, nullable=True)         # tips / insights

    generated_at    = Column(DateTime, default=datetime.utcnow, nullable=False)

    # ── Relationships ─────────────────────────────────
    user = relationship("User", back_populates="health_analyses")

    def __repr__(self):
        return f"<HealthAnalysis id={self.id} user_id={self.user_id}>"