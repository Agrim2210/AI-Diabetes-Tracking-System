import io
from datetime import datetime
from typing import List

import matplotlib
matplotlib.use("Agg")  # non-interactive backend — required for server environments
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table,
    TableStyle, Image as RLImage, HRFlowable,
)
from sqlalchemy.orm import Session

from api.db import models
from api.db.models import RiskLevel
from api.schemas.history import (
    PaginatedHistory, HistoryItem,
    TrendOut, TrendPoint,
    AnalysisOut,
)


# ── Helpers ───────────────────────────────────────────────────────────────────

RISK_ORDER = {RiskLevel.LOW: 0, RiskLevel.MEDIUM: 1, RiskLevel.HIGH: 2}


def _fetch_user_predictions(user_id: int, db: Session) -> List[models.Prediction]:
    """Return all predictions for a user, ordered oldest → newest."""
    return (
        db.query(models.Prediction)
        .filter(models.Prediction.user_id == user_id)
        .order_by(models.Prediction.predicted_at.asc())
        .all()
    )


# ── Paginated History ─────────────────────────────────────────────────────────

def get_paginated_history(
    user_id: int,
    page: int,
    page_size: int,
    db: Session,
) -> PaginatedHistory:
    """
    Return a paginated list of predictions for a user.
    Sorted newest first for display.
    """
    query = (
        db.query(models.Prediction)
        .filter(models.Prediction.user_id == user_id)
        .order_by(models.Prediction.predicted_at.desc())
    )
    total = query.count()
    records = query.offset((page - 1) * page_size).limit(page_size).all()

    items = []
    for r in records:
        items.append(HistoryItem(
            id=r.id,
            result=r.result,
            probability=r.probability,
            risk_level=r.risk_level,
            advice=r.advice,
            predicted_at=r.predicted_at,
            Pregnancies=r.pregnancies,
            Glucose=r.glucose,
            BloodPressure=r.blood_pressure,
            SkinThickness=r.skin_thickness,
            Insulin=r.insulin,
            BMI=r.bmi,
            DiabetesPedigreeFunction=r.diabetes_pedigree_function,
            Age=r.age,
        ))

    return PaginatedHistory(total=total, page=page, page_size=page_size, items=items)


# ── Trend Data ────────────────────────────────────────────────────────────────

def get_trend_data(user_id: int, db: Session) -> TrendOut:
    """
    Build time-series trend data from all predictions.
    Returned as a list of TrendPoint objects — consumed by Chart.js on the frontend.
    """
    records = _fetch_user_predictions(user_id, db)

    points = [
        TrendPoint(
            predicted_at=r.predicted_at,
            glucose=r.glucose,
            bmi=r.bmi,
            blood_pressure=r.blood_pressure,
            risk_level=r.risk_level,
            probability=r.probability,
        )
        for r in records
    ]

    return TrendOut(total_records=len(points), points=points)


# ── Health Analysis ───────────────────────────────────────────────────────────

def _determine_risk_progression(records: List[models.Prediction]) -> str:
    """
    Compare the average risk score of the first half vs second half of records.
    Returns: "Improving" | "Worsening" | "Stable"
    """
    if len(records) < 2:
        return "Stable"

    scores = [RISK_ORDER[r.risk_level] for r in records]
    mid = len(scores) // 2
    first_half_avg = sum(scores[:mid]) / mid
    second_half_avg = sum(scores[mid:]) / (len(scores) - mid)

    delta = second_half_avg - first_half_avg
    if delta < -0.3:
        return "Improving"
    elif delta > 0.3:
        return "Worsening"
    return "Stable"


def _build_insights(
    avg_glucose: float,
    avg_bmi: float,
    avg_bp: float,
    risk_progression: str,
) -> str:
    """Build a human-readable health insights paragraph."""
    insights = []

    if avg_glucose and avg_glucose > 140:
        insights.append(
            f"Your average glucose ({avg_glucose:.1f} mg/dL) is above the healthy threshold. "
            "Consider a low-glycaemic diet and consult your doctor."
        )
    elif avg_glucose:
        insights.append(f"Your average glucose ({avg_glucose:.1f} mg/dL) is within a healthy range.")

    if avg_bmi and avg_bmi > 25:
        insights.append(
            f"Your average BMI ({avg_bmi:.1f}) indicates being overweight. "
            "Regular physical activity can significantly reduce diabetes risk."
        )

    if avg_bp and avg_bp > 90:
        insights.append(
            f"Your average blood pressure ({avg_bp:.1f} mmHg) is elevated. "
            "Reducing sodium intake and managing stress can help."
        )

    if risk_progression == "Improving":
        insights.append("Great news — your overall risk trend is improving. Keep up your healthy habits!")
    elif risk_progression == "Worsening":
        insights.append(
            "Your risk trend is worsening over time. "
            "Please schedule a consultation with a healthcare professional."
        )
    else:
        insights.append("Your risk level has been stable. Continue monitoring your health regularly.")

    return " ".join(insights)


def get_health_analysis(user_id: int, db: Session) -> AnalysisOut:
    """
    Analyse all predictions for a user and return aggregate health insights.
    Saves a snapshot to the health_analyses table.
    """
    records = _fetch_user_predictions(user_id, db)

    if not records:
        now = datetime.utcnow()
        return AnalysisOut(
            total_predictions=0,
            diabetic_count=0,
            non_diabetic_count=0,
            avg_glucose=None,
            avg_bmi=None,
            avg_blood_pressure=None,
            risk_progression=None,
            trend_summary="No predictions found. Make your first prediction to see your health analysis.",
            health_insights=None,
            generated_at=now,
        )

    total = len(records)
    diabetic = sum(1 for r in records if r.result == 1)
    non_diabetic = total - diabetic

    avg_glucose = round(sum(r.glucose for r in records) / total, 2)
    avg_bmi = round(sum(r.bmi for r in records) / total, 2)
    avg_bp = round(sum(r.blood_pressure for r in records) / total, 2)

    risk_progression = _determine_risk_progression(records)

    trend_summary = (
        f"You have made {total} prediction(s). "
        f"{diabetic} indicated diabetic risk and {non_diabetic} did not. "
        f"Your health trend is: {risk_progression}."
    )

    health_insights = _build_insights(avg_glucose, avg_bmi, avg_bp, risk_progression)

    # Persist snapshot
    analysis = models.HealthAnalysis(
        user_id=user_id,
        total_predictions=total,
        diabetic_count=diabetic,
        non_diabetic_count=non_diabetic,
        avg_glucose=avg_glucose,
        avg_bmi=avg_bmi,
        avg_blood_pressure=avg_bp,
        risk_progression=risk_progression,
        trend_summary=trend_summary,
        health_insights=health_insights,
        generated_at=datetime.utcnow(),
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    return AnalysisOut.model_validate(analysis)


# ── Chart Generators ──────────────────────────────────────────────────────────

def _make_line_chart(
    dates: list,
    values: list,
    title: str,
    ylabel: str,
    color: str = "#1a73e8",
) -> io.BytesIO:
    """Render a line chart and return it as a PNG BytesIO buffer."""
    fig, ax = plt.subplots(figsize=(7, 2.8))
    ax.plot(dates, values, marker="o", color=color, linewidth=1.8, markersize=4)
    ax.set_title(title, fontsize=11, fontweight="bold", pad=8)
    ax.set_ylabel(ylabel, fontsize=9)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    fig.autofmt_xdate(rotation=30)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.spines[["top", "right"]].set_visible(False)
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=140, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf


def _make_risk_bar_chart(records: List[models.Prediction]) -> io.BytesIO:
    """Render a stacked risk-level bar chart over time."""
    df = pd.DataFrame([
        {"date": r.predicted_at.date(), "risk": r.risk_level.value}
        for r in records
    ])
    counts = df.groupby(["date", "risk"]).size().unstack(fill_value=0)
    for col in ["Low", "Medium", "High"]:
        if col not in counts.columns:
            counts[col] = 0
    counts = counts[["Low", "Medium", "High"]]

    fig, ax = plt.subplots(figsize=(7, 2.8))
    counts.plot(
        kind="bar", stacked=True, ax=ax,
        color={"Low": "#34a853", "Medium": "#fbbc04", "High": "#ea4335"},
        width=0.6,
    )
    ax.set_title("Risk Level Distribution Over Time", fontsize=11, fontweight="bold", pad=8)
    ax.set_xlabel("")
    ax.set_ylabel("Count", fontsize=9)
    ax.legend(loc="upper right", fontsize=8)
    ax.spines[["top", "right"]].set_visible(False)
    plt.xticks(rotation=30, fontsize=8)
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=140, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf


# ── PDF Report ────────────────────────────────────────────────────────────────

def generate_pdf_report(user: models.User, db: Session) -> io.BytesIO:
    """
    Build a full PDF health report for the given user and return it as a BytesIO buffer.
    Sections:
        1. Header — patient info
        2. Summary stats
        3. Trend charts (Glucose, BMI, Risk distribution)
        4. Prediction history table
        5. Health analysis & insights
    """
    records = _fetch_user_predictions(user.id, db)
    analysis_out = get_health_analysis(user.id, db)

    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        pdf_buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "Title", parent=styles["Title"], fontSize=18, spaceAfter=6
    )
    heading_style = ParagraphStyle(
        "Heading", parent=styles["Heading2"], fontSize=13, spaceAfter=4, textColor=colors.HexColor("#1a73e8")
    )
    body_style = styles["BodyText"]
    body_style.fontSize = 9

    story = []

    # ── 1. Header ─────────────────────────────────────────────────────────────
    story.append(Paragraph("AI Diabetes Health Report", title_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1a73e8")))
    story.append(Spacer(1, 0.3 * cm))

    generated = datetime.utcnow().strftime("%B %d, %Y at %H:%M UTC")
    story.append(Paragraph(f"<b>Patient:</b> {user.full_name or user.username}", body_style))
    story.append(Paragraph(f"<b>Username:</b> {user.username}", body_style))
    story.append(Paragraph(f"<b>Report Generated:</b> {generated}", body_style))
    story.append(Spacer(1, 0.5 * cm))

    # ── 2. Summary Stats ──────────────────────────────────────────────────────
    story.append(Paragraph("Summary", heading_style))
    summary_data = [
        ["Total Predictions", "Diabetic", "Non-Diabetic", "Risk Trend"],
        [
            str(analysis_out.total_predictions),
            str(analysis_out.diabetic_count),
            str(analysis_out.non_diabetic_count),
            analysis_out.risk_progression or "N/A",
        ],
    ]
    summary_table = Table(summary_data, colWidths=[4 * cm] * 4)
    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a73e8")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f8f9fa"), colors.white]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#dee2e6")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 0.5 * cm))

    # ── 3. Charts ─────────────────────────────────────────────────────────────
    if records:
        dates = [r.predicted_at for r in records]
        glucoses = [r.glucose for r in records]
        bmis = [r.bmi for r in records]

        story.append(Paragraph("Trend Charts", heading_style))

        glucose_buf = _make_line_chart(dates, glucoses, "Glucose Over Time", "Glucose (mg/dL)", "#ea4335")
        story.append(RLImage(glucose_buf, width=14 * cm, height=5.5 * cm))
        story.append(Spacer(1, 0.3 * cm))

        bmi_buf = _make_line_chart(dates, bmis, "BMI Over Time", "BMI", "#34a853")
        story.append(RLImage(bmi_buf, width=14 * cm, height=5.5 * cm))
        story.append(Spacer(1, 0.3 * cm))

        risk_buf = _make_risk_bar_chart(records)
        story.append(RLImage(risk_buf, width=14 * cm, height=5.5 * cm))
        story.append(Spacer(1, 0.5 * cm))

    # ── 4. History Table ──────────────────────────────────────────────────────
    story.append(Paragraph("Prediction History", heading_style))
    table_headers = ["Date", "Glucose", "BMI", "BP", "Result", "Risk", "Probability"]
    table_data = [table_headers]

    for r in reversed(records):  # newest first
        table_data.append([
            r.predicted_at.strftime("%Y-%m-%d"),
            f"{r.glucose:.1f}",
            f"{r.bmi:.1f}",
            f"{r.blood_pressure:.1f}",
            "Diabetic" if r.result == 1 else "No Diabetes",
            r.risk_level.value,
            f"{r.probability * 100:.1f}%",
        ])

    history_table = Table(table_data, colWidths=[2.4 * cm, 2.2 * cm, 1.8 * cm, 1.8 * cm, 2.8 * cm, 2.0 * cm, 2.5 * cm])
    history_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a73e8")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f8f9fa"), colors.white]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#dee2e6")),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(history_table)
    story.append(Spacer(1, 0.5 * cm))

    # ── 5. Health Insights ────────────────────────────────────────────────────
    story.append(Paragraph("Health Analysis & Insights", heading_style))
    story.append(Paragraph(analysis_out.trend_summary or "", body_style))
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph(analysis_out.health_insights or "", body_style))
    story.append(Spacer(1, 0.5 * cm))

    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey))
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph(
        "<i>This report is generated by an AI system and is not a medical diagnosis. "
        "Always consult a qualified healthcare professional.</i>",
        ParagraphStyle("Disclaimer", parent=body_style, fontSize=7.5, textColor=colors.grey),
    ))

    doc.build(story)
    pdf_buffer.seek(0)
    return pdf_buffer