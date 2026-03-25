from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from api.db.models import RiskLevel


class HistoryItem(BaseModel):
    """Single prediction record in the history list."""
    id: int
    result: int
    probability: float
    risk_level: RiskLevel
    advice: Optional[str]
    predicted_at: datetime

    Pregnancies: int
    Glucose: float
    BloodPressure: float
    SkinThickness: float
    Insulin: float
    BMI: float
    DiabetesPedigreeFunction: float
    Age: int

    model_config = {"from_attributes": True}


class TrendPoint(BaseModel):
    """Single data point for trend charts (sent to Chart.js on frontend)."""
    predicted_at: datetime
    glucose: float
    bmi: float
    blood_pressure: float
    risk_level: RiskLevel
    probability: float


class TrendOut(BaseModel):
    """Full trend data payload for the history/trends endpoint."""
    total_records: int
    points: List[TrendPoint]


class AnalysisOut(BaseModel):
    """Health analysis summary returned by /history/analysis."""
    total_predictions: int
    diabetic_count: int
    non_diabetic_count: int

    avg_glucose: Optional[float]
    avg_bmi: Optional[float]
    avg_blood_pressure: Optional[float]

    risk_progression: Optional[str]    # "Improving" / "Worsening" / "Stable"
    trend_summary: Optional[str]
    health_insights: Optional[str]

    generated_at: datetime

    model_config = {"from_attributes": True}


class PaginatedHistory(BaseModel):
    """Paginated wrapper for GET /history/me."""
    total: int
    page: int
    page_size: int
    items: List[HistoryItem]