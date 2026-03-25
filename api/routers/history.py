from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from api.core.dependencies import get_db, get_current_user
from api.db import models
from api.schemas.history import PaginatedHistory, TrendOut, AnalysisOut
from api.services.analysis_service import (
    get_paginated_history,
    get_trend_data,
    get_health_analysis,
    generate_pdf_report,
)

router = APIRouter(prefix="/history", tags=["History"])


# ── Paginated Prediction History ──────────────────────────────────────────────

@router.get("/me", response_model=PaginatedHistory)
def my_history(
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=10, ge=1, le=50, description="Records per page"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Return paginated list of all past predictions for the logged-in user.
    Sorted by most recent first.
    """
    return get_paginated_history(
        user_id=current_user.id,
        page=page,
        page_size=page_size,
        db=db,
    )


# ── Trend Data for Charts ─────────────────────────────────────────────────────

@router.get("/trends", response_model=TrendOut)
def trends(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Return time-series data for the frontend Chart.js graphs.
    Includes: Glucose, BMI, BloodPressure, risk_level, probability over time.
    """
    return get_trend_data(user_id=current_user.id, db=db)


# ── AI Health Analysis ────────────────────────────────────────────────────────

@router.get("/analysis", response_model=AnalysisOut)
def analysis(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Analyse the full prediction history and return:
    - Aggregate stats (avg glucose, BMI, blood pressure)
    - Risk progression trend (Improving / Worsening / Stable)
    - Human-readable health insights
    Saves the analysis snapshot to the DB for audit.
    """
    return get_health_analysis(user_id=current_user.id, db=db)


# ── PDF Report Export ─────────────────────────────────────────────────────────

@router.get("/report/pdf")
def export_pdf(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Generate and stream a PDF health report containing:
    - Patient summary
    - Full prediction history table
    - Trend charts (Glucose, BMI, risk level over time)
    - Health analysis and insights
    """
    pdf_buffer = generate_pdf_report(user=current_user, db=db)

    filename = f"diabetes_report_{current_user.username}.pdf"
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )