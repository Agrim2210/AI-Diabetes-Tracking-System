import pandas as pd
import joblib
import numpy as np
from pathlib import Path
from sqlalchemy.orm import Session

from api.db import models
from api.db.models import RiskLevel
from api.schemas.prediction import PatientData

# ── Model Loading ─────────────────────────────────────────────

BASE_DIR = Path(__file__).resolve().parent.parent.parent

_model = None
_expected_cols = None


def _load_artifacts():
    global _model, _expected_cols

    if _model is None:
        _model = joblib.load(BASE_DIR / "model" / "random_forest_model.pkl")

    if _expected_cols is None:
        _expected_cols = joblib.load(BASE_DIR / "model" / "columns.pkl")


# ── Feature Engineering ───────────────────────────────────────

def _engineer_features(patient_data: PatientData) -> np.ndarray:
    MEDIANS = {
    "Glucose":       117.0,
    "BloodPressure":  72.0,
    "SkinThickness":  28.0,   
    "Insulin":       102.5,   
    "BMI":            32.0,
    }  
    

    # Replace None AND zero with median (matches training zero-replacement)
    preg = patient_data.Pregnancies
    gluc = patient_data.Glucose       if (patient_data.Glucose       is not None and patient_data.Glucose       > 0) else MEDIANS["Glucose"]
    bp   = patient_data.BloodPressure if (patient_data.BloodPressure is not None and patient_data.BloodPressure > 0) else MEDIANS["BloodPressure"]
    skin = patient_data.SkinThickness if (patient_data.SkinThickness is not None and patient_data.SkinThickness > 0) else MEDIANS["SkinThickness"]
    ins  = patient_data.Insulin       if (patient_data.Insulin       is not None and patient_data.Insulin       > 0) else MEDIANS["Insulin"]
    bmi  = patient_data.BMI           if (patient_data.BMI           is not None and patient_data.BMI           > 0) else MEDIANS["BMI"]
    dpf  = float(patient_data.DiabetesPedigreeFunction)
    age  = patient_data.Age

    # ── BMI Category ─────────────────────────────────────────────
    if bmi < 18.5:
        bmi_cat = "Underweight"
    elif bmi < 25:
        bmi_cat = "Normal"
    elif bmi < 30:
        bmi_cat = "Overweight"
    else:
        bmi_cat = "Obese"

    # ── Age Group (Middle is baseline — dropped during training) ─
    if age < 30:
        age_group = "Young"
    elif age < 50:
        age_group = "Middle"   # baseline — both Age_Group_Old=0, Age_Group_Young=0
    else:
        age_group = "Old"

    # ── Glucose Level (must match training thresholds exactly) ───
    if gluc < 100:
        gluc_level = "Normal"
    elif gluc < 140:
        gluc_level = "Prediabetes"
    else:
        gluc_level = "Diabetes"   # baseline — gets dropped by get_dummies

    # ── Interaction Feature ──────────────────────────────────────
    bmi_age = float(bmi * age)

    # ── Build DataFrame ──────────────────────────────────────────
    row = pd.DataFrame([{
        "Pregnancies":              float(preg),
        "Glucose":                  float(gluc),
        "BloodPressure":            float(bp),
        "SkinThickness":            float(skin),
        "Insulin":                  float(ins),
        "BMI":                      float(bmi),
        "DiabetesPedigreeFunction": float(dpf),
        "Age":                      float(age),
        "BMI_Category":             bmi_cat,
        "Age_Group":                age_group,
        "Glucose_Level":            gluc_level,
        "BMI_Age_Interaction":      float(bmi_age),
    }])

    # ── One-hot encode categoricals ──────────────────────────────
    row = pd.get_dummies(row, columns=["BMI_Category", "Age_Group", "Glucose_Level"])

    # ── Align to exact training column order ─────────────────────
    for col in _expected_cols:
        if col not in row.columns:
            row[col] = 0

    row = row[_expected_cols]

    # Force every column to float — prevents string conversion errors
    row = row.apply(pd.to_numeric, errors='coerce').fillna(0).astype(float)

    # ── Debug ─────────────────────────────────────────────────────
    print("=== FEATURE DEBUG ===")
    print(f"  gluc={gluc}, bmi={bmi}, ins={ins}, age={age}")
    print(f"  gluc_level={gluc_level}, bmi_cat={bmi_cat}, age_group={age_group}")
    print(f"  Shape: {row.shape}")
    print(row.to_string())
    print("=====================")

    return row.values


# ── Risk Labeling ─────────────────────────────────────────────

def _assign_risk_level(probability: float) -> RiskLevel:
    if probability < 0.35:
        return RiskLevel.LOW
    elif probability < 0.65:
        return RiskLevel.MEDIUM
    else:
        return RiskLevel.HIGH


# ── Health Advice ─────────────────────────────────────────────

def _generate_advice(risk_level: RiskLevel, patient_data: PatientData) -> str:
    tips = []

    if patient_data.Glucose and patient_data.Glucose > 140:
        tips.append("Your glucose is critically high. Seek medical attention immediately.")
    elif patient_data.Glucose and patient_data.Glucose > 126:
        tips.append("Your glucose is elevated. Reduce sugar and refined carbohydrate intake.")

    if patient_data.BMI and patient_data.BMI > 30:
        tips.append("Your BMI indicates obesity. Regular exercise and a calorie-controlled diet are essential.")
    elif patient_data.BMI and patient_data.BMI > 25:
        tips.append("Your BMI is above normal. Aim for 30 minutes of moderate exercise daily.")

    if patient_data.BloodPressure and patient_data.BloodPressure > 90:
        tips.append("Your blood pressure is high. Reduce salt intake and manage stress.")

    if patient_data.Insulin and patient_data.Insulin > 150:
        tips.append("Your insulin level is high. Consult your doctor about insulin resistance.")

    base = {
        RiskLevel.LOW:    "Your risk of diabetes is currently low. Maintain a healthy lifestyle.",
        RiskLevel.MEDIUM: "You have a moderate risk of diabetes. Regular check-ups and lifestyle changes are recommended.",
        RiskLevel.HIGH:   "You have a high risk of diabetes. Please consult a healthcare professional as soon as possible.",
    }[risk_level]

    return base + (" Specific recommendations: " + " ".join(tips) if tips else "")


# ── Core Prediction Function ──────────────────────────────────

def run_prediction(
    patient_data: PatientData,
    user_id: int,
    db: Session,
) -> models.Prediction:

    _load_artifacts()

    features    = _engineer_features(patient_data)
    result      = int(_model.predict(features)[0])
    probability = float(_model.predict_proba(features)[0][1])

    print(f">>> result={result}, probability={probability:.4f}")

    risk_level = _assign_risk_level(probability)
    advice     = _generate_advice(risk_level, patient_data)

    prediction = models.Prediction(
        user_id=user_id,
        pregnancies=patient_data.Pregnancies,
        glucose=patient_data.Glucose,
        blood_pressure=patient_data.BloodPressure,
        skin_thickness=patient_data.SkinThickness,
        insulin=patient_data.Insulin,
        bmi=patient_data.BMI,
        diabetes_pedigree_function=patient_data.DiabetesPedigreeFunction,
        age=patient_data.Age,
        result=result,
        probability=probability,
        risk_level=risk_level,
        advice=advice,
    )

    try:
        db.add(prediction)
        db.commit()
        db.refresh(prediction)
    except Exception:
        db.rollback()
        raise

    return prediction