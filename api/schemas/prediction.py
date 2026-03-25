from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional
from api.db.models import RiskLevel


class PatientData(BaseModel):
    """Input schema — matches your existing ML model's expected features."""
    Pregnancies: int
    Glucose: float
    BloodPressure: float
    SkinThickness: float
    Insulin: float
    BMI: float
    DiabetesPedigreeFunction: float
    Age: int

    @field_validator("Glucose", "BloodPressure", "BMI")
    @classmethod
    def must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Value must be greater than 0.")
        return v

    @field_validator("Age", "Pregnancies")
    @classmethod
    def must_be_non_negative(cls, v: int) -> int:
        if v < 0:
            raise ValueError("Value cannot be negative.")
        return v
    @field_validator("Glucose")
    @classmethod
    def glucose_range(cls, v: float) -> float:
        if v > 600:
            raise ValueError("Glucose value is unrealistically high. Max is 600 mg/dL.")
        return v
    
    @field_validator("BMI")
    @classmethod
    def bmi_range(cls, v: float) -> float:
        if v > 80:
            raise ValueError("BMI value is unrealistically high. Max is 80.")
        return v

from pydantic import BaseModel, model_validator

class PredictionOut(BaseModel):
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

    @model_validator(mode="before")
    @classmethod
    def map_orm_fields(cls, obj):
        if isinstance(obj, dict):
            return obj
        return {
            "id":                       obj.id,
            "result":                   obj.result,
            "probability":              obj.probability,
            "risk_level":               obj.risk_level,
            "advice":                   obj.advice,
            "predicted_at":             obj.predicted_at,
            "Pregnancies":              obj.pregnancies,
            "Glucose":                  obj.glucose,
            "BloodPressure":            obj.blood_pressure,
            "SkinThickness":            obj.skin_thickness,
            "Insulin":                  obj.insulin,
            "BMI":                      obj.bmi,
            "DiabetesPedigreeFunction": obj.diabetes_pedigree_function,
            "Age":                      obj.age,
        }
            